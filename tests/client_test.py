# -*- coding: utf-8 -*-

import yadisk

from yadisk._common import is_operation_link, ensure_path_has_schema, remove_path_schema
from yadisk._api import GetOperationStatusRequest

import hashlib
import logging
import os
import platform
import posixpath
import sys
import tempfile

from io import BytesIO
from typing import Any

import pytest

__all__ = ["TestClient"]

replay_disabled = os.environ.get("PYTHON_YADISK_REPLAY_ENABLED", "1") != "1"
recording_enabled = os.environ.get("PYTHON_YADISK_RECORDING_ENABLED", "0") == "1"


def open_tmpfile(mode):
    if platform.system() == "Windows" and sys.version_info >= (3, 12):
        # This is needed in order to work on Windows
        return tempfile.NamedTemporaryFile(mode, delete_on_close=False)
    else:
        return tempfile.NamedTemporaryFile(mode)


class TestClient:
    @pytest.mark.skipif(
        replay_disabled,
        reason="this test is not meant to run outside of replay mode, it must be modified first"
    )
    @pytest.mark.usefixtures("record_or_replay")
    def test_get_disk_info(self, client: yadisk.Client) -> None:
        disk_info = client.get_disk_info()

        assert isinstance(disk_info, yadisk.objects.DiskInfoObject)
        assert disk_info.user is not None

        # If you re-record this test, you'll have to put your account data here
        assert disk_info.user.login == "ivknv"
        assert disk_info.field("reg_time").year == 2017

    @pytest.mark.usefixtures("sync_client_test")
    def test_get_meta(self, client: yadisk.Client, disk_root: str) -> None:
        resource = client.get_meta(disk_root)

        assert isinstance(resource, yadisk.objects.ResourceObject)
        assert resource.type == "dir"
        assert resource.name == posixpath.split(disk_root)[1]

        # Test the convenience method as well
        assert resource.get_meta(".").resource_id == resource.resource_id

    @pytest.mark.usefixtures("sync_client_test")
    def test_listdir(self, client: yadisk.Client, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3"]

        for name in names:
            path = posixpath.join(disk_root, name)

            client.mkdir(path)

        contents = list(client.listdir(disk_root))
        result = [i.name for i in contents]

        assert result == names

        # Test the convenience method as well
        for dir in contents:
            assert list(dir.listdir(".")) == []

    @pytest.mark.usefixtures("sync_client_test")
    def test_listdir_fields(self, client: yadisk.Client, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3"]

        for name in names:
            path = posixpath.join(disk_root, name)

            client.mkdir(path)

        result = [(i.name, i.type, i.file) for i in client.listdir(disk_root, fields=["name", "type"])]

        assert result == [(name, "dir", None) for name in names]

    @pytest.mark.usefixtures("sync_client_test")
    def test_listdir_on_file(self, client: yadisk.Client, disk_root: str) -> None:
        buf = BytesIO()
        buf.write(b"0" * 1000)
        buf.seek(0)

        path = posixpath.join(disk_root, "zeroes.txt")

        client.upload(buf, path)

        with pytest.raises(yadisk.exceptions.WrongResourceTypeError):
            list(client.listdir(path))

    @pytest.mark.usefixtures("sync_client_test")
    def test_listdir_with_limits(self, client: yadisk.Client, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3"]

        for name in names:
            path = posixpath.join(disk_root, name)

            client.mkdir(path)

        result = [i.name for i in client.listdir(disk_root, limit=1)]

        assert result == names

    @pytest.mark.usefixtures("sync_client_test")
    def test_listdir_with_max_items(self, client: yadisk.Client, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3", "dir4", "dir5", "dir6"]

        for name in names:
            path = posixpath.join(disk_root, name)

            client.mkdir(path)

        results = [
            [i.name for i in client.listdir(disk_root, max_items=0)],
            [i.name for i in client.listdir(disk_root, max_items=1, limit=1)],
            [i.name for i in client.listdir(disk_root, max_items=2, limit=1)],
            [i.name for i in client.listdir(disk_root, max_items=3, limit=1)],
            [i.name for i in client.listdir(disk_root, max_items=10, limit=1)],
        ]

        expected = [
            [],
            names[:1],
            names[:2],
            names[:3],
            names[:10],
        ]

        assert results == expected

    @pytest.mark.usefixtures("sync_client_test")
    def test_mkdir_and_exists(self, client: yadisk.Client, disk_root: str) -> None:
        names = ["dir1", "dir2"]

        for name in names:
            path = posixpath.join(disk_root, name)

            client.mkdir(path)
            assert client.exists(path)

            client.remove(path, permanently=True)
            assert not client.exists(path)

    def _test_makedirs(self, client: yadisk.Client, disk_root: str) -> None:
        parent1 = posixpath.join(disk_root, "parent1")
        parent2 = posixpath.join(parent1, "parent2")
        parent3 = posixpath.join(parent2, "parent3")

        path1 = posixpath.join(parent3, "leaf_directory")
        path2 = posixpath.join(parent3, "another_directory")
        path3 = posixpath.join(disk_root, "directory")

        for path in [parent1, parent2, parent3, path1, path2, path3]:
            assert not client.exists(path)

        client.makedirs(path1)
        assert client.is_dir(path1)

        with pytest.raises(yadisk.exceptions.DirectoryExistsError):
            client.makedirs(path1)

        client.makedirs(path2)
        assert client.is_dir(path2)

        client.makedirs(path3)
        assert client.is_dir(path3)

    @pytest.mark.usefixtures("sync_client_test")
    def test_makedirs_without_schema(self, client: yadisk.Client, disk_root: str) -> None:
        self._test_makedirs(client, remove_path_schema(disk_root)[1])

    @pytest.mark.usefixtures("sync_client_test")
    def test_makedirs_with_schema(self, client: yadisk.Client, disk_root: str) -> None:
        self._test_makedirs(client, ensure_path_has_schema(disk_root, "disk"))

    @pytest.mark.skipif(
        platform.system() == "Windows" and sys.version_info < (3, 12),
        reason="won't work on Windows with Python < 3.12"
    )
    @pytest.mark.usefixtures("sync_client_test")
    def test_upload_and_download(self, client: yadisk.Client, disk_root: str) -> None:
        with open_tmpfile("w+b") as buf1, open_tmpfile("w+b") as buf2:
            buf1.write(b"0" * 1024**2)
            buf1.seek(0)

            path = posixpath.join(disk_root, "zeroes.txt")

            client.upload(buf1.name, path, overwrite=True)
            client.download(path, buf2.name)

            buf1.seek(0)
            buf2.seek(0)

            assert buf1.read() == buf2.read()

    @pytest.mark.usefixtures("sync_client_test")
    def test_check_token(self, client: yadisk.Client, disk_root: str) -> None:
        assert client.check_token()
        assert not client.check_token("asdasdasd")

    @pytest.mark.usefixtures("sync_client_test")
    def test_permanent_remove(self, client: yadisk.Client, disk_root: str) -> None:
        path = posixpath.join(disk_root, "dir")
        origin_path = "disk:" + path

        client.mkdir(path)
        client.remove(path, permanently=True)

        for i in client.trash_listdir("/"):
            assert i.origin_path != origin_path

    @pytest.mark.usefixtures("sync_client_test")
    def test_restore_trash(self, client: yadisk.Client, disk_root: str) -> None:
        path = posixpath.join(disk_root, "dir")
        origin_path = "disk:" + path

        client.mkdir(path)
        client.remove(path)

        trash_path: Any = None

        for i in client.trash_listdir("/"):
            if i.origin_path == origin_path:
                assert i.exists()
                assert i.is_dir()
                assert not i.is_file()

                trash_path = i.path
                break

        assert trash_path is not None

        client.restore_trash(trash_path, path)
        assert client.exists(path)

    @pytest.mark.usefixtures("sync_client_test")
    def test_move(self, client: yadisk.Client, disk_root: str) -> None:
        path1 = posixpath.join(disk_root, "dir1")
        path2 = posixpath.join(disk_root, "dir2")
        client.mkdir(path1)
        client.move(path1, path2)

        assert client.exists(path2)

    @pytest.mark.usefixtures("sync_client_test")
    def test_rename(self, client: yadisk.Client, disk_root: str) -> None:
        filename1 = "dir1"
        filename2 = "dir2/"

        path1 = posixpath.join(disk_root, filename1)
        path2 = posixpath.join(disk_root, filename2)

        assert not client.exists(path1)
        assert not client.exists(path2)

        dir = client.mkdir(path1)

        assert dir.is_dir()
        rename_result = dir.rename(filename2)

        assert isinstance(rename_result, yadisk.objects.SyncResourceLinkObject)
        dir = rename_result

        assert not client.exists(path1)
        assert dir.is_dir()

        for bad_filename in ("", ".", "..", "/", "something/else"):
            with pytest.raises(ValueError):
                dir.rename(bad_filename)

    def test_rename_edgecases(self, client: yadisk.Client, mocker) -> None:
        # Test a few edgecases, make sure the destination paths are correct
        # Path schemas must be preserved

        dst_paths = []

        def mock_move(src_path: str, dst_path: str, **kwargs) -> None:
            # Store the destination path for later checking
            dst_paths.append(dst_path)

        mocker.patch.object(client, "move", mock_move)

        with pytest.raises(ValueError):
            client.rename("", "impossible")

        with pytest.raises(ValueError):
            client.rename("/", "impossible")

        with pytest.raises(ValueError):
            client.rename("////", "impossible")

        with pytest.raises(ValueError):
            client.rename("disk:/", "impossible")

        with pytest.raises(ValueError):
            client.rename("app:/", "another_directory")

        client.rename("disk:", "not_a_schema")
        client.rename("disk:/asd.txt", "renamed.txt")
        client.rename("asd.txt", "renamed.txt")
        client.rename("disk:/directory/file1.txt", "renamed_file.txt")
        client.rename("disk:/directory/", "renamed_dir")

        assert dst_paths == [
            "not_a_schema", "disk:/renamed.txt", "renamed.txt",
            "disk:/directory/renamed_file.txt", "disk:/renamed_dir"
        ]

    @pytest.mark.usefixtures("sync_client_test")
    def test_remove_trash(self, client: yadisk.Client, disk_root: str) -> None:
        path = posixpath.join(disk_root, "dir-to-remove")
        origin_path = "disk:" + path

        client.mkdir(path)
        client.remove(path)

        trash_path: Any = None

        for i in client.trash_listdir("/"):
            if i.origin_path == origin_path:
                trash_path = i.path
                break

        assert trash_path is not None

        client.remove_trash(trash_path)
        assert not client.trash_exists(trash_path)

    @pytest.mark.usefixtures("sync_client_test")
    def test_publish_unpublish(self, client: yadisk.Client, disk_root: str) -> None:
        client.publish(disk_root)

        meta = client.get_meta(disk_root)
        assert meta.public_url is not None
        assert meta.public_key is not None

        public_key, public_url = meta.public_key, meta.public_url

        assert client.is_public_dir(public_key)
        assert client.is_public_dir(public_url)
        assert not client.is_public_file(public_key)
        assert not client.is_public_file(public_url)

        client.unpublish(disk_root)

        meta = client.get_meta(disk_root)
        assert meta.public_url is None
        assert meta.public_key is None

        assert not client.is_public_dir(public_key)
        assert not client.is_public_dir(public_url)
        assert not client.is_public_file(public_key)
        assert not client.is_public_file(public_url)

    @pytest.mark.usefixtures("sync_client_test")
    def test_public_settings(self, client: yadisk.Client, disk_root: str) -> None:
        client.publish(disk_root)
        public_url = client.get_meta(disk_root) @ "public_url"

        # First, set a password
        client.update_public_settings(disk_root, {
            "password": "1234"
        })

        with pytest.raises(yadisk.exceptions.PasswordRequiredError):
            client.get_public_download_link(public_url)

        # We will make the public resource link expire by updating the settings
        available_until = 1
        client.update_public_settings(disk_root, {
            "password": "1234",
            "available_until": available_until
        })

        # As of writing, the endpoint returns only "available_until"
        settings = client.get_public_settings(disk_root)

        assert settings.available_until == available_until

        # At this point the public link should no longer be valid
        with pytest.raises(yadisk.exceptions.PathNotFoundError):
            client.get_public_meta(public_url)

        client.unpublish(disk_root)

    @pytest.mark.usefixtures("sync_client_test")
    def test_patch(self, client: yadisk.Client, disk_root: str) -> None:
        directory = client.patch(disk_root, {"test_property": "I'm a value!"})
        assert directory.custom_properties == {"test_property": "I'm a value!"}

        directory = client.patch(disk_root, {"number": 42})
        assert directory.custom_properties == {"test_property": "I'm a value!", "number": 42}

        directory = directory.patch({"test_property": None, "number": None})
        assert directory.custom_properties is None

    @pytest.mark.usefixtures("sync_client_test")
    def test_issue7(self, client: yadisk.Client, disk_root: str) -> None:
        # See https://github.com/ivknv/yadisk/issues/7

        try:
            list(client.public_listdir("any value here", path="any value here"))
        except yadisk.exceptions.PathNotFoundError:
            pass

    def test_is_operation_link(self) -> None:
        assert is_operation_link("https://cloud-api.yandex.net/v1/disk/operations/123asd")
        assert is_operation_link("http://cloud-api.yandex.net/v1/disk/operations/123asd")
        assert not is_operation_link("https://cloud-api.yandex.net/v1/disk/operation/1283718")
        assert not is_operation_link("https://asd8iaysd89asdgiu")
        assert not is_operation_link("http://asd8iaysd89asdgiu")

    def test_get_operation_status_request_url(self, client: yadisk.Client, disk_root: str) -> None:
        request = GetOperationStatusRequest(
            client.session,
            "https://cloud-api.yandex.net/v1/disk/operations/123asd")
        assert is_operation_link(request.url)

        request = GetOperationStatusRequest(
            client.session,
            "http://cloud-api.yandex.net/v1/disk/operations/123asd")
        assert is_operation_link(request.url)
        assert request.url.startswith("https://")

        request = GetOperationStatusRequest(
            client.session,
            "https://asd8iaysd89asdgiu")
        assert is_operation_link(request.url)
        assert request.url.startswith("https://")

    def test_ensure_path_has_schema(self) -> None:
        # See https://github.com/ivknv/yadisk/issues/26 for more details

        assert ensure_path_has_schema("disk:") == "disk:/disk:"
        assert ensure_path_has_schema("trash:", default_schema="trash") == "trash:/trash:"
        assert ensure_path_has_schema("/asd:123") == "disk:/asd:123"
        assert ensure_path_has_schema("/asd:123", "trash") == "trash:/asd:123"
        assert ensure_path_has_schema("example/path") == "disk:/example/path"
        assert ensure_path_has_schema("app:/test") == "app:/test"

    @pytest.mark.usefixtures("sync_client_test")
    def test_upload_download_non_seekable(
        self,
        client: yadisk.Client,
        disk_root: str,
        mocker
    ) -> None:
        # It should be possible to upload/download non-seekable file objects (such as sys.stdin/sys.stdout)
        # See https://github.com/ivknv/yadisk/pull/31 for more details

        def seek(*args, **kwargs):
            raise NotImplementedError

        test_input_file = BytesIO(b"0" * 1000)
        mocker.patch.object(test_input_file, "seekable", lambda: False)
        mocker.patch.object(test_input_file, "seek", seek)

        test_input_file.seek = seek  # type: ignore

        dst_path = posixpath.join(disk_root, "zeroes.txt")

        client.upload(test_input_file, dst_path, n_retries=50)

        test_output_file = BytesIO()
        mocker.patch.object(test_output_file, "seekable", lambda: False)
        mocker.patch.object(test_output_file, "seek", seek)

        client.download(dst_path, test_output_file, n_retries=50)

        assert test_input_file.tell() == 1000
        assert test_output_file.tell() == 1000

    @pytest.mark.usefixtures("sync_client_test")
    def test_upload_generator(self, client: yadisk.Client, disk_root: str) -> None:
        data = b"0" * 1000

        def payload():
            yield data[:500]
            yield data[500:]

        dst_path = posixpath.join(disk_root, "zeroes.txt")

        output = BytesIO()

        client.upload(payload, dst_path).download(output)

        output.seek(0)

        assert output.read() == data

    @pytest.mark.usefixtures("sync_client_test")
    def test_copy(
        self,
        client: yadisk.Client,
        disk_root: str,
        poll_interval: float
    ) -> None:
        dir = client.mkdir(posixpath.join(disk_root, "directory_to_copy"))
        dir.upload(BytesIO(b"example text"), "file.txt")
        dir.mkdir("nested directory 1")
        dir.mkdir("nested directory 2")

        dst_path = posixpath.join(disk_root, "directory_copy")

        dir.copy(dst_path, poll_interval=poll_interval)

        copy_info = client.get_meta(dst_path)

        assert copy_info.embedded is not None
        assert copy_info.embedded.items is not None

        contents = sorted([(resource.type, resource.name) for resource in copy_info.embedded.items])

        expected_contents = [
            ("dir", "nested directory 1"),
            ("dir", "nested directory 2"),
            ("file", "file.txt"),
        ]

        assert copy_info.type == "dir"
        assert contents == expected_contents

    @pytest.mark.usefixtures("sync_client_test")
    def test_save_to_disk(
        self,
        client: yadisk.Client,
        disk_root: str,
        poll_interval: float
    ) -> None:
        test_contents = b"test file contents"

        public_file_path = posixpath.join(disk_root, "public_file.txt")
        client.upload(BytesIO(test_contents), public_file_path)

        client.publish(public_file_path)

        public_file_info = client.get_meta(public_file_path)

        assert public_file_info.public_url is not None

        client.save_to_disk(
            public_file_info.public_url,
            name="saved_public_file.txt",
            save_path=disk_root,
            poll_interval=poll_interval
        )

        saved_file_path = posixpath.join(disk_root, "saved_public_file.txt")
        saved_file_info = client.get_meta(saved_file_path)

        assert saved_file_info.md5 == hashlib.md5(test_contents).hexdigest() == public_file_info.md5

    @pytest.mark.usefixtures("sync_client_test")
    def test_upload_url(
        self,
        client: yadisk.Client,
        disk_root: str,
        poll_interval: float
    ) -> None:
        test_contents = b"test file contents"

        file_path = posixpath.join(disk_root, "example_file.txt")
        dst_path = posixpath.join(disk_root, "uploaded_from_url.txt")

        client.upload(BytesIO(test_contents), file_path)
        download_link = client.get_download_link(file_path)

        client.upload_url(download_link, dst_path, poll_interval=poll_interval)

        dst_file_info = client.get_meta(dst_path)
        assert dst_file_info.md5 == hashlib.md5(test_contents).hexdigest()

    @pytest.mark.usefixtures("record_or_replay")
    def test_none_args(self, client: yadisk.Client) -> None:
        # Passing headers=None, <session_name>_args=None should not trigger any errors

        assert client.check_token(
            headers=None,
            requests_args=None,
            httpx_args=None,
            curl_options=None
        )

        link = "https://downloader.disk.yandex.ru/disk/4deb67f875582dfa8dd53c5d3b72e8fb49ce7cc1502765175dc3af1183a575b6/668ddef2/nsHIkeXKnaRGpTyn0UiRqaUl8Jt3QPRPLeFAjvpBi81sWp-27VfwQ64jjvznGt8kNwE-ofj0cgVKPtPiYwpOA%3D%3D?uid=455675172&filename=CsVGRa8itZzMzH19HCCF4ceXpFpwJAUHpCRAqGOb4O6I59R-oDeDyKMqTq8daIAvY89CJ64noQqRebmQ3C08d8%3D&disposition=attachment&hash=&limit=0&contenttype=application%2Foctet-stream&owneruid=455675172&fsize=72&hid=3e96286ac2b9f0703688be31e7dd0843&media_type=data&tknv=v2&etag=747ce618999f04e43b6435ab69d7108a"

        # This is worth testing on download_by_link() as well, since it has
        # slightly different logic
        with pytest.raises((yadisk.exceptions.GoneError, yadisk.exceptions.InternalServerError)):
            client.download_by_link(
                link,
                BytesIO(),
                headers=None,
                requests_args=None,
                httpx_args=None,
                curl_options=None
            )

    @pytest.mark.usefixtures("record_or_replay")
    def test_get_files(self, client: yadisk.Client) -> None:
        files = list(client.get_files(max_items=25))

        assert len(files) <= 25

        for file in files:
            assert file.is_file()

        offset = 15
        files_with_offset = list(client.get_files(max_items=10, offset=offset))

        assert len(files_with_offset) <= 10

        for file in files_with_offset:
            assert file.is_file()

        assert [file @ "path" for file in files[offset:]] == [file @ "path" for file in files_with_offset]

        assert len(list(client.get_files(max_items=10, limit=3))) <= 10

    @pytest.mark.usefixtures("sync_client_test")
    def test_get_last_uploaded(self, client: yadisk.Client, disk_root: str) -> None:
        files_to_upload = [
            ("first.txt", b"example content"),
            ("second.txt", b"this is the second file"),
            ("third.txt", b"this is the third file")
        ]

        for filename, content in files_to_upload:
            client.upload(BytesIO(content), posixpath.join(disk_root, filename))

        for uploaded_file, (filename, content) in zip(client.get_last_uploaded(limit=3), files_to_upload[::-1]):
            assert uploaded_file.path == "disk:" + posixpath.join(disk_root, filename)

            output = BytesIO()
            uploaded_file.download(output)

            output.seek(0)
            assert output.read() == content

    @pytest.mark.usefixtures("sync_client_test")
    def test_public_listdir(self, client: yadisk.Client, disk_root: str) -> None:
        directory = client.mkdir(posixpath.join(disk_root, "public"))
        directory.publish()

        public_directory = directory.get_meta()

        assert public_directory.is_dir()
        assert public_directory.public_key is not None
        assert client.is_public_dir(public_directory.public_key)

        files_to_upload = [
            ("first.txt", b"example content"),
            ("second.txt", b"this is the second file"),
            ("third.txt", b"this is the third file")
        ]

        for filename, content in files_to_upload:
            public_directory.upload(BytesIO(content), filename).publish()

        public_files = list(public_directory.public_listdir(sort="modified"))

        for file, (filename, content) in zip(public_files, files_to_upload):
            assert file.name == filename
            assert client.is_public_file(public_directory.public_key, path=file.path)

            output = BytesIO()
            client.download_public(public_directory.public_key, output, path=file.path)

            output.seek(0)
            assert output.read() == content

        public_directory.unpublish()
        assert not client.is_public_dir(public_directory.public_key)

    @pytest.mark.skipif(
        recording_enabled,
        reason="before recording this test, ensure it's not a privacy concern for you"
    )
    @pytest.mark.usefixtures("record_or_replay")
    def test_get_public_resources(self, client: yadisk.Client) -> None:
        first_10 = list(client.get_all_public_resources(max_items=10, limit=3))
        with_offset = list(client.get_all_public_resources(max_items=5, offset=5, limit=2))

        for public_resource in first_10 + with_offset:
            assert client.public_exists(public_resource @ "public_key")

        assert [i.path for i in first_10[5:]] == [i.path for i in with_offset]

    @pytest.mark.usefixtures("sync_client_test")
    def test_get_upload_link_object(self, client: yadisk.Client, disk_root: str) -> None:
        directory = client.get_meta(disk_root)
        upload_link = directory.get_upload_link_object("test.txt")

        assert client.get_operation_status(upload_link @ "operation_id") == "in-progress"

        client.upload_by_link(BytesIO(b"test file"), upload_link @ "href")

        assert client.get_operation_status(upload_link @ "operation_id") == "success"

    @pytest.mark.usefixtures("record_or_replay")
    def test_streaming_requests(self, client: yadisk.Client) -> None:
        # stream=True should not break requests

        assert client.check_token(stream=True)
        assert len(client.get_last_uploaded(stream=True, limit=10, fields=["items.type"])) == 10

    @pytest.mark.usefixtures("sync_client_test")
    def test_wait_for_operation(
        self,
        client: yadisk.Client,
        disk_root: str,
        poll_interval: float,
        mocker
    ) -> None:
        directory = client.mkdir("directory")
        operation = directory.remove(permanently=True, force_async=True, wait=False)

        with pytest.raises(yadisk.exceptions.AsyncOperationPollingTimeoutError):
            operation.wait(poll_timeout=0.0)

        operation.wait(poll_interval=poll_interval)

        assert operation.get_status() == "success"

        # Mock get_operation_status() to trigger an AsyncOperationFailedError
        mocker.patch.object(client, "get_operation_status", lambda *args, **kwargs: "failed")

        with pytest.raises(yadisk.exceptions.AsyncOperationFailedError):
            operation.wait(poll_interval=poll_interval)

    @pytest.mark.usefixtures("record_or_replay")
    def test_download_by_link_error(self, client: yadisk.Client) -> None:
        # Make sure that if the server returns a bad status code (e.g. 500),
        # download_by_link() will not write the response into the file

        # Sample link, should either produce a 500 or 410 error
        # In case of error it outputs an HTML page, rather than a file
        link = "https://downloader.disk.yandex.ru/disk/4deb67f875582dfa8dd53c5d3b72e8fb49ce7cc1502765175dc3af1183a575b6/668ddef2/nsHIkeXKnaRGpTyn0UiRqaUl8Jt3QPRPLeFAjvpBi81sWp-27VfwQ64jjvznGt8kNwE-ofj0cgVKPtPiYwpOA%3D%3D?uid=455675172&filename=CsVGRa8itZzMzH19HCCF4ceXpFpwJAUHpCRAqGOb4O6I59R-oDeDyKMqTq8daIAvY89CJ64noQqRebmQ3C08d8%3D&disposition=attachment&hash=&limit=0&contenttype=application%2Foctet-stream&owneruid=455675172&fsize=72&hid=3e96286ac2b9f0703688be31e7dd0843&media_type=data&tknv=v2&etag=747ce618999f04e43b6435ab69d7108a"

        output = BytesIO()

        with pytest.raises((yadisk.exceptions.GoneError, yadisk.exceptions.InternalServerError)):
            client.download_by_link(link, output, n_retries=5)

        output.seek(0)
        assert output.read() == b""

    @pytest.mark.usefixtures("sync_client_test")
    def test_operation_error_triggers_retry(
        self,
        client: yadisk.Client,
        disk_root: str,
        poll_interval: float,
        mocker,
        caplog
    ) -> None:
        path1 = posixpath.join(disk_root, "test_file.txt")
        path2 = posixpath.join(disk_root, "copy.txt")
        client.upload(BytesIO(b"test data"), path1)


        class GetOperationStatusMock:
            def __init__(self):
                self.call_count_since_success = 0

            def __call__(self, *args, **kwargs) -> yadisk.types.OperationStatus:
                status = yadisk.Client.get_operation_status(client, *args, **kwargs)

                if status == "success":
                    self.call_count_since_success += 1

                    if self.call_count_since_success < 3:
                        return "failed"

                return status


        mocker.patch.object(client, "get_operation_status", GetOperationStatusMock())

        with caplog.at_level(logging.INFO, logger="yadisk"):
            client.copy(
                path1,
                path2,
                force_async=True,
                overwrite=True,
                poll_interval=poll_interval
            )

        expected_message1 = "automatic retry triggered: (1 out of 50), got AsyncOperationFailedError: Asynchronous operation failed"  # noqa: E501
        expected_message2 = "asynchronous operation failed, attempting to restart it"
        assert expected_message1 in caplog.text
        assert caplog.text.count(expected_message2) >= 2

        assert client.is_file(path2)
