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

    @pytest.mark.usefixtures("async_client_test")
    async def test_listdir(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        names = ["dir1", "dir2", "dir3"]
        paths = [posixpath.join(disk_root, name) for name in names]

        for path in paths:
            await async_client.mkdir(path)

        async def get_result():
            return [i.name async for i in async_client.listdir(disk_root)]

        result = await get_result()

        assert result == names

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
        path = disk_root

        await async_client.patch(path, {"test_property": "I'm a value!"})

        props: Any = (await async_client.get_meta(path)).custom_properties
        assert props is not None
        assert props["test_property"] == "I'm a value!"

        await async_client.patch(path, {"test_property": None})
        assert (await async_client.get_meta(path)).custom_properties is None

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
    async def test_upload_download_non_seekable(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        # It should be possible to upload/download non-seekable file objects (such as stdin/stdout)
        # See https://github.com/ivknv/yadisk/pull/31 for more details

        test_input_file = BytesIO(b"0" * 1000)
        test_input_file.seekable = lambda: False  # type: ignore

        def seek(*args, **kwargs):
            raise NotImplementedError

        test_input_file.seek = seek  # type: ignore

        dst_path = posixpath.join(disk_root, "zeroes.txt")

        await async_client.upload(test_input_file, dst_path, n_retries=50)

        test_output_file = BytesIO()
        test_output_file.seekable = lambda: False  # type: ignore
        test_output_file.seek = seek  # type: ignore

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
