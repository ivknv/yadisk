# -*- coding: utf-8 -*-

import hashlib
import tempfile
from typing import Any
import aiofiles

import os
import platform
import posixpath
from io import BytesIO
import sys

import yadisk
from yadisk._common import is_operation_link, ensure_path_has_schema
from yadisk._api import GetOperationStatusRequest

import pytest

__all__ = ["TestAsyncClient"]

replay_disabled = os.environ.get("PYTHON_YADISK_REPLAY_ENABLED", "1") != "1"
recording_enabled = os.environ.get("PYTHON_YADISK_RECORDING_ENABLED", "0") == "1"


def open_tmpfile(mode):
    if platform.system() == "Windows" and sys.version_info >= (3, 12):
        # This is needed in order to work on Windows
        return tempfile.NamedTemporaryFile(mode, delete_on_close=False)
    else:
        return tempfile.NamedTemporaryFile(mode)


def async_open_tmpfile(mode):
    if platform.system() == "Windows" and sys.version_info >= (3, 12):
        # This is needed in order to work on Windows
        return aiofiles.tempfile.NamedTemporaryFile(mode, delete_on_close=False)
    else:
        return aiofiles.tempfile.NamedTemporaryFile(mode)


@pytest.mark.anyio
class TestAsyncClient:
    @pytest.mark.skipif(
        replay_disabled,
        reason="this test is not meant to run outside of replay mode, it must be modified first"
    )
    @pytest.mark.usefixtures("record_or_replay")
    async def test_get_disk_info(self, async_client: yadisk.AsyncClient) -> None:
        disk_info = await async_client.get_disk_info()

        assert isinstance(disk_info, yadisk.objects.DiskInfoObject)
        assert disk_info.user is not None

        # If you re-record this test, you'll have to put your account data here
        assert disk_info.user.login == "ivknv"
        assert disk_info.field("reg_time").year == 2017

    @pytest.mark.usefixtures("async_client_test")
    async def test_get_meta(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        resource = await async_client.get_meta(disk_root)

        assert isinstance(resource, yadisk.objects.ResourceObject)
        assert resource.type == "dir"
        assert resource.name == posixpath.split(disk_root)[1]

        # Test convenience method as well
        assert (await resource.get_meta(".")).resource_id == resource.resource_id

    @pytest.mark.usefixtures("async_client_test")
    async def test_listdir(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3"]
        paths = [posixpath.join(disk_root, name) for name in names]

        for path in paths:
            await async_client.mkdir(path)

        contents = [i async for i in async_client.listdir(disk_root)]
        result = [i.name for i in contents]

        assert result == names

        # Test the convenience method as well
        for dir in contents:
            assert [i async for i in dir.listdir(".")] == []

    @pytest.mark.usefixtures("async_client_test")
    async def test_listdir_fields(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3"]
        paths = [posixpath.join(disk_root, name) for name in names]

        for path in paths:
            await async_client.mkdir(path)

        async def get_result():
            return [(i.name, i.type, i.file)
                    async for i in async_client.listdir(disk_root, fields=["name", "type"])]

        result = await get_result()

        assert result == [(name, "dir", None) for name in names]

    @pytest.mark.usefixtures("async_client_test")
    async def test_listdir_on_file(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        buf = BytesIO()
        buf.write(b"0" * 1000)
        buf.seek(0)

        path = posixpath.join(disk_root, "zeroes.txt")

        await async_client.upload(buf, path)

        with pytest.raises(yadisk.exceptions.WrongResourceTypeError):
            [i async for i in async_client.listdir(path)]

    @pytest.mark.usefixtures("async_client_test")
    async def test_listdir_with_limits(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3"]
        paths = [posixpath.join(disk_root, name) for name in names]

        for path in paths:
            await async_client.mkdir(path)

        async def get_result():
            return [i.name async for i in async_client.listdir(disk_root, limit=1)]

        result = await get_result()

        assert result == names

    @pytest.mark.usefixtures("async_client_test")
    async def test_listdir_with_max_items(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3", "dir4", "dir5", "dir6"]

        for name in names:
            path = posixpath.join(disk_root, name)

            await async_client.mkdir(path)

        results = [
            [i.name async for i in async_client.listdir(disk_root, max_items=0)],
            [i.name async for i in async_client.listdir(disk_root, max_items=1, limit=1)],
            [i.name async for i in async_client.listdir(disk_root, max_items=2, limit=1)],
            [i.name async for i in async_client.listdir(disk_root, max_items=3, limit=1)],
            [i.name async for i in async_client.listdir(disk_root, max_items=10, limit=1)],
        ]

        expected = [
            [],
            names[:1],
            names[:2],
            names[:3],
            names[:10],
        ]

        assert results == expected

    @pytest.mark.usefixtures("async_client_test")
    async def test_mkdir_and_exists(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3"]
        paths = [posixpath.join(disk_root, name) for name in names]

        async def check_existence(path):
            await async_client.mkdir(path)
            assert await async_client.exists(path)

            await async_client.remove(path, permanently=True)
            assert not await async_client.exists(path)

        for path in paths:
            await check_existence(path)

    @pytest.mark.skipif(
        platform.system() == "Windows" and sys.version_info < (3, 12),
        reason="won't work on Windows with Python < 3.12"
    )
    @pytest.mark.usefixtures("async_client_test")
    async def test_upload_and_download(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        with BytesIO() as buf1, open_tmpfile("w+b") as buf2:
            buf1.write(b"0" * 1024**2)
            buf1.seek(0)

            path = posixpath.join(disk_root, "zeroes.txt")

            await async_client.upload(buf1, path, overwrite=True, n_retries=50)
            await async_client.download(path, buf2.name, n_retries=50)

            buf1.seek(0)
            buf2.seek(0)

            assert buf1.read() == buf2.read()

    @pytest.mark.skipif(
        platform.system() == "Windows" and sys.version_info < (3, 12),
        reason="won't work on Windows with Python < 3.12"
    )
    @pytest.mark.usefixtures("async_client_test")
    async def test_upload_and_download_async(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        content = b"0" * 1024 ** 2
        async with async_open_tmpfile("wb+") as source:
            await source.write(content)
            await source.seek(0)

            path1 = posixpath.join(disk_root, "zeroes.txt")
            path2 = posixpath.join(disk_root, "zeroes_from_generator.txt")

            await async_client.upload(source, path1, overwrite=True, n_retries=50)

            async def source_generator():
                for _ in range(1024):
                    yield b"0" * 1024

            await async_client.upload(source_generator, path2, overwrite=True, n_retries=50)

        async with async_open_tmpfile("wb+") as destination:
            await async_client.download(path1, destination, n_retries=50)
            await destination.seek(0)

            assert content == await destination.read()

            await destination.seek(0)
            await destination.truncate()
            await async_client.download(path2, destination, n_retries=50)
            await destination.seek(0)

            assert content == await destination.read()

    @pytest.mark.usefixtures("async_client_test")
    async def test_check_token(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        assert await async_client.check_token()
        assert not await async_client.check_token("asdasdasd")

    @pytest.mark.usefixtures("async_client_test")
    async def test_permanent_remove(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        path = posixpath.join(disk_root, "dir")
        origin_path = "disk:" + path

        await async_client.mkdir(path)
        await async_client.remove(path, permanently=True)

        async for i in async_client.trash_listdir("/"):
            assert i.origin_path != origin_path

    @pytest.mark.usefixtures("async_client_test")
    async def test_restore_trash(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        path = posixpath.join(disk_root, "dir")
        origin_path = "disk:" + path

        await async_client.mkdir(path)
        await async_client.remove(path)

        trash_path: Any = None

        async for i in async_client.trash_listdir("/"):
            if i.origin_path == origin_path:
                trash_path = i.path
                break

        assert trash_path is not None

        await async_client.restore_trash(trash_path, path)
        assert await async_client.exists(path)

    @pytest.mark.usefixtures("async_client_test")
    async def test_move(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        path1 = posixpath.join(disk_root, "dir1")
        path2 = posixpath.join(disk_root, "dir2")
        await async_client.mkdir(path1)
        await async_client.move(path1, path2)

        assert await async_client.exists(path2)

    @pytest.mark.usefixtures("async_client_test")
    async def test_rename(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        filename1 = "dir1"
        filename2 = "dir2/"

        path1 = posixpath.join(disk_root, filename1)
        path2 = posixpath.join(disk_root, filename2)

        assert not await async_client.exists(path1)
        assert not await async_client.exists(path2)

        dir = await async_client.mkdir(path1)

        assert await dir.is_dir()
        rename_result = await dir.rename(filename2)

        assert isinstance(rename_result, yadisk.objects.AsyncResourceLinkObject)
        dir = rename_result

        assert not await async_client.exists(path1)
        assert await dir.is_dir()

        for bad_filename in ("", ".", "..", "/", "something/else"):
            with pytest.raises(ValueError):
                await dir.rename(bad_filename)

    @pytest.mark.usefixtures("async_client_test")
    async def test_remove_trash(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        path = posixpath.join(disk_root, "dir-to-remove")
        origin_path = "disk:" + path

        await async_client.mkdir(path)
        await async_client.remove(path)

        trash_path: Any = None

        async for i in async_client.trash_listdir("/"):
            if i.origin_path == origin_path:
                trash_path = i.path
                break

        assert trash_path is not None

        await async_client.remove_trash(trash_path)
        assert not await async_client.trash_exists(trash_path)

    @pytest.mark.usefixtures("async_client_test")
    async def test_publish_unpublish(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        path = disk_root

        await async_client.publish(path)
        assert (await async_client.get_meta(path)).public_url is not None

        await async_client.unpublish(path)
        assert (await async_client.get_meta(path)).public_url is None

    @pytest.mark.usefixtures("async_client_test")
    async def test_patch(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        directory = await async_client.patch(disk_root, {"test_property": "I'm a value!"})
        assert directory.custom_properties is not None

        assert directory.custom_properties["test_property"] == "I'm a value!"

        directory = await directory.patch({"test_property": None})
        assert directory.custom_properties is None

    @pytest.mark.usefixtures("async_client_test")
    async def test_issue7(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        # See https://github.com/ivknv/yadisk/issues/7

        try:
            [i async for i in async_client.public_listdir("any value here", path="any value here")]
        except yadisk.exceptions.PathNotFoundError:
            pass

    def test_is_operation_link(self) -> None:
        assert is_operation_link("https://cloud-api.yandex.net/v1/disk/operations/123asd")
        assert is_operation_link("http://cloud-api.yandex.net/v1/disk/operations/123asd")
        assert not is_operation_link("https://cloud-api.yandex.net/v1/disk/operation/1283718")
        assert not is_operation_link("https://asd8iaysd89asdgiu")
        assert not is_operation_link("http://asd8iaysd89asdgiu")

    async def test_get_operation_status_request_url(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        request = GetOperationStatusRequest(
            async_client.session,
            "https://cloud-api.yandex.net/v1/disk/operations/123asd")
        assert is_operation_link(request.url)

        request = GetOperationStatusRequest(
            async_client.session,
            "http://cloud-api.yandex.net/v1/disk/operations/123asd")
        assert is_operation_link(request.url)
        assert request.url.startswith("https://")

        request = GetOperationStatusRequest(
            async_client.session,
            "https://asd8iaysd89asdgiu")
        assert is_operation_link(request.url)
        assert request.url.startswith("https://")

    @pytest.mark.usefixtures("async_client_test")
    async def test_is_file(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        # See https://github.com/ivknv/yadisk-async/pull/6
        buf1 = BytesIO()

        buf1.write(b"0" * 1024**2)
        buf1.seek(0)

        path = posixpath.join(disk_root, "zeroes.txt")

        await async_client.upload(buf1, path, overwrite=True, n_retries=50)
        assert await async_client.is_file(path)

    def test_ensure_path_has_schema(self) -> None:
        # See https://github.com/ivknv/yadisk/issues/26 for more details

        assert ensure_path_has_schema("disk:") == "disk:/disk:"
        assert ensure_path_has_schema("trash:", default_schema="trash") == "trash:/trash:"
        assert ensure_path_has_schema("/asd:123") == "disk:/asd:123"
        assert ensure_path_has_schema("/asd:123", "trash") == "trash:/asd:123"
        assert ensure_path_has_schema("example/path") == "disk:/example/path"
        assert ensure_path_has_schema("app:/test") == "app:/test"

    @pytest.mark.usefixtures("async_client_test")
    async def test_upload_download_non_seekable(
        self,
        async_client: yadisk.AsyncClient,
        disk_root: str,
        mocker
    ) -> None:
        # It should be possible to upload/download non-seekable file objects (such as stdin/stdout)
        # See https://github.com/ivknv/yadisk/pull/31 for more details

        def seek(*args, **kwargs):
            raise NotImplementedError

        test_input_file = BytesIO(b"0" * 1000)
        mocker.patch.object(test_input_file, "seekable", lambda: False)
        mocker.patch.object(test_input_file, "seek", seek)

        dst_path = posixpath.join(disk_root, "zeroes.txt")

        await async_client.upload(test_input_file, dst_path, n_retries=50)

        test_output_file = BytesIO()
        mocker.patch.object(test_output_file, "seekable", lambda: False)
        mocker.patch.object(test_output_file, "seek", seek)

        await async_client.download(dst_path, test_output_file, n_retries=50)

        assert test_input_file.tell() == 1000
        assert test_output_file.tell() == 1000

    @pytest.mark.usefixtures("async_client_test")
    async def test_copy(
        self,
        async_client: yadisk.AsyncClient,
        disk_root: str,
        poll_interval: float
    ) -> None:
        dir = await async_client.mkdir(posixpath.join(disk_root, "directory_to_copy"))
        await dir.upload(BytesIO(b"example text"), "file.txt")
        await dir.mkdir("nested directory 1")
        await dir.mkdir("nested directory 2")

        dst_path = posixpath.join(disk_root, "directory_copy")

        await dir.copy(dst_path, poll_interval=poll_interval)

        copy_info = await async_client.get_meta(dst_path)

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

    @pytest.mark.usefixtures("async_client_test")
    async def test_save_to_disk(
        self,
        async_client: yadisk.AsyncClient,
        disk_root: str,
        poll_interval: float
    ) -> None:
        test_contents = b"test file contents"

        public_file_path = posixpath.join(disk_root, "public_file.txt")
        await async_client.upload(BytesIO(test_contents), public_file_path)

        await async_client.publish(public_file_path)

        public_file_info = await async_client.get_meta(public_file_path)

        assert public_file_info.public_url is not None

        await async_client.save_to_disk(
            public_file_info.public_url,
            name="saved_public_file.txt",
            save_path=disk_root,
            poll_interval=poll_interval
        )

        saved_file_path = posixpath.join(disk_root, "saved_public_file.txt")
        saved_file_info = await async_client.get_meta(saved_file_path)

        assert saved_file_info.md5 == hashlib.md5(test_contents).hexdigest() == public_file_info.md5

    @pytest.mark.usefixtures("async_client_test")
    async def test_upload_url(
        self,
        async_client: yadisk.AsyncClient,
        disk_root: str,
        poll_interval: float
    ) -> None:
        test_contents = b"test file contents"

        file_path = posixpath.join(disk_root, "example_file.txt")
        dst_path = posixpath.join(disk_root, "uploaded_from_url.txt")

        await async_client.upload(BytesIO(test_contents), file_path)
        download_link = await async_client.get_download_link(file_path)

        await async_client.upload_url(download_link, dst_path, poll_interval=poll_interval)

        dst_file_info = await async_client.get_meta(dst_path)
        assert dst_file_info.md5 == hashlib.md5(test_contents).hexdigest()

    @pytest.mark.usefixtures("record_or_replay")
    async def test_none_args(self, async_client: yadisk.AsyncClient) -> None:
        # Passing headers=None, <session_name>_args=None should not trigger any errors

        assert await async_client.check_token(
            headers=None,
            requests_args=None,
            httpx_args=None,
            curl_options=None
        )

        link = "https://downloader.disk.yandex.ru/disk/4deb67f875582dfa8dd53c5d3b72e8fb49ce7cc1502765175dc3af1183a575b6/668ddef2/nsHIkeXKnaRGpTyn0UiRqaUl8Jt3QPRPLeFAjvpBi81sWp-27VfwQ64jjvznGt8kNwE-ofj0cgVKPtPiYwpOA%3D%3D?uid=455675172&filename=CsVGRa8itZzMzH19HCCF4ceXpFpwJAUHpCRAqGOb4O6I59R-oDeDyKMqTq8daIAvY89CJ64noQqRebmQ3C08d8%3D&disposition=attachment&hash=&limit=0&contenttype=application%2Foctet-stream&owneruid=455675172&fsize=72&hid=3e96286ac2b9f0703688be31e7dd0843&media_type=data&tknv=v2&etag=747ce618999f04e43b6435ab69d7108a"

        # This is worth testing on download_by_link() as well, since it has
        # slightly different logic
        with pytest.raises(yadisk.exceptions.GoneError):
            await async_client.download_by_link(
                link,
                BytesIO(),
                headers=None,
                requests_args=None,
                httpx_args=None,
                curl_options=None
            )

    @pytest.mark.usefixtures("record_or_replay")
    async def test_get_files(self, async_client: yadisk.AsyncClient) -> None:
        files = [i async for i in async_client.get_files(max_items=25)]

        assert len(files) <= 25

        for file in files:
            assert await file.is_file()

        offset = 15
        files_with_offset = [i async for i in async_client.get_files(max_items=10, offset=offset)]

        assert len(files_with_offset) <= 10

        for file in files_with_offset:
            assert await file.is_file()

        assert [file @ "path" for file in files[offset:]] == [file @ "path" for file in files_with_offset]

        assert len([i async for i in async_client.get_files(max_items=10, limit=3)]) <= 10

    @pytest.mark.usefixtures("async_client_test")
    async def test_get_last_uploaded(
        self,
        async_client: yadisk.AsyncClient,
        disk_root: str
    ) -> None:
        files_to_upload = [
            ("first.txt", b"example content"),
            ("second.txt", b"this is the second file"),
            ("third.txt", b"this is the third file")
        ]

        for filename, content in files_to_upload:
            await async_client.upload(BytesIO(content), posixpath.join(disk_root, filename))

        last_uploaded = await async_client.get_last_uploaded(limit=3)

        for uploaded_file, (filename, content) in zip(last_uploaded, files_to_upload[::-1]):
            assert uploaded_file.path == "disk:" + posixpath.join(disk_root, filename)

            output = BytesIO()
            await uploaded_file.download(output)

            output.seek(0)
            assert output.read() == content

    @pytest.mark.usefixtures("async_client_test")
    async def test_public_listdir(
        self,
        async_client: yadisk.AsyncClient,
        disk_root: str
    ) -> None:
        directory = await async_client.mkdir(posixpath.join(disk_root, "public"))
        await directory.publish()

        public_directory = await directory.get_meta()

        assert await public_directory.is_dir()
        assert public_directory.public_key is not None
        assert await async_client.is_public_dir(public_directory.public_key)

        files_to_upload = [
            ("first.txt", b"example content"),
            ("second.txt", b"this is the second file"),
            ("third.txt", b"this is the third file")
        ]

        for filename, content in files_to_upload:
            await (await public_directory.upload(BytesIO(content), filename)).publish()

        public_files = [i async for i in public_directory.public_listdir(sort="modified")]

        for file, (filename, content) in zip(public_files, files_to_upload):
            assert file.name == filename
            assert await async_client.is_public_file(public_directory.public_key, path=file.path)

            output = BytesIO()
            await async_client.download_public(public_directory.public_key, output, path=file.path)

            output.seek(0)
            assert output.read() == content

        await public_directory.unpublish()
        assert not await async_client.is_public_dir(public_directory.public_key)

    @pytest.mark.skipif(
        recording_enabled,
        reason="before recording this test, ensure it's not a privacy concern for you"
    )
    @pytest.mark.usefixtures("record_or_replay")
    async def test_get_public_resources(self, async_client: yadisk.AsyncClient) -> None:
        first_10 = (await async_client.get_public_resources(limit=10)).items
        with_offset = (await async_client.get_public_resources(limit=5, offset=5)).items

        assert first_10 is not None
        assert with_offset is not None

        for public_resource in first_10 + with_offset:
            print(f"{public_resource @ 'path'}")
            assert await async_client.public_exists(public_resource @ "public_key")

        assert [i.path for i in first_10[5:]] == [i.path for i in with_offset]

    @pytest.mark.usefixtures("async_client_test")
    async def test_get_upload_link_object(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        directory = await async_client.get_meta(disk_root)
        upload_link = await directory.get_upload_link_object("test.txt")

        assert (
            await async_client.get_operation_status(upload_link @ "operation_id")
        ) == "in-progress"

        await async_client.upload_by_link(BytesIO(b"test file"), upload_link @ "href")

        assert (
            await async_client.get_operation_status(upload_link @ "operation_id")
        ) == "success"

    @pytest.mark.usefixtures("record_or_replay")
    async def test_streaming_requests(self, async_client: yadisk.AsyncClient) -> None:
        # stream=True should not break requests

        assert await async_client.check_token(stream=True)
        assert len(
            await async_client.get_last_uploaded(
                stream=True, limit=10, fields=["items.type"]
            )
        ) == 10

    @pytest.mark.usefixtures("async_client_test")
    async def test_wait_for_operation(
        self,
        async_client: yadisk.AsyncClient,
        disk_root: str,
        poll_interval: float,
        mocker
    ) -> None:
        directory = await async_client.mkdir("directory")
        operation = await directory.remove(permanently=True, force_async=True, wait=False)

        with pytest.raises(yadisk.exceptions.AsyncOperationPollingTimeoutError):
            await operation.wait(poll_timeout=0.0)

        await operation.wait(poll_interval=poll_interval)

        assert await operation.get_status() == "success"

        # Mock get_operation_status() to trigger an AsyncOperationFailedError
        async def fake_get_operation_status(*args, **kwargs) -> yadisk.types.OperationStatus:
            return "failed"

        mocker.patch.object(async_client, "get_operation_status", fake_get_operation_status)

        with pytest.raises(yadisk.exceptions.AsyncOperationFailedError):
            await operation.wait(poll_interval=poll_interval)

    @pytest.mark.usefixtures("record_or_replay")
    async def test_download_by_link_error(self, async_client: yadisk.AsyncClient) -> None:
        # Make sure that if the server returns a bad status code (e.g. 500),
        # download_by_link() will not write the response into the file

        # Sample link, should either produce a 500 or 410 error
        # In case of error it outputs an HTML page, rather than a file
        link = "https://downloader.disk.yandex.ru/disk/4deb67f875582dfa8dd53c5d3b72e8fb49ce7cc1502765175dc3af1183a575b6/668ddef2/nsHIkeXKnaRGpTyn0UiRqaUl8Jt3QPRPLeFAjvpBi81sWp-27VfwQ64jjvznGt8kNwE-ofj0cgVKPtPiYwpOA%3D%3D?uid=455675172&filename=CsVGRa8itZzMzH19HCCF4ceXpFpwJAUHpCRAqGOb4O6I59R-oDeDyKMqTq8daIAvY89CJ64noQqRebmQ3C08d8%3D&disposition=attachment&hash=&limit=0&contenttype=application%2Foctet-stream&owneruid=455675172&fsize=72&hid=3e96286ac2b9f0703688be31e7dd0843&media_type=data&tknv=v2&etag=747ce618999f04e43b6435ab69d7108a"

        output = BytesIO()

        with pytest.raises((yadisk.exceptions.GoneError, yadisk.exceptions.InternalServerError)):
            await async_client.download_by_link(link, output)

        output.seek(0)
        assert output.read() == b""
