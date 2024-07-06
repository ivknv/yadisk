# -*- coding: utf-8 -*-

import tempfile
from typing import Any
import aiofiles

import platform
import posixpath
from io import BytesIO
import sys

import yadisk
from yadisk._common import is_operation_link, ensure_path_has_schema
from yadisk._api import GetOperationStatusRequest

import pytest

__all__ = ["TestAsyncClient"]


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

    @pytest.mark.usefixtures("async_client_test")
    async def test_upload_and_download(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        if platform.system() == "Windows" and sys.version_info < (3, 12):
            pytest.skip("won't work on Windows with Python < 3.12")
            return

        with BytesIO() as buf1, open_tmpfile("w+b") as buf2:
            buf1.write(b"0" * 1024**2)
            buf1.seek(0)

            path = posixpath.join(disk_root, "zeroes.txt")

            await async_client.upload(buf1, path, overwrite=True, n_retries=50)
            await async_client.download(path, buf2.name, n_retries=50)

            buf1.seek(0)
            buf2.seek(0)

            assert buf1.read() == buf2.read()

    @pytest.mark.usefixtures("async_client_test")
    async def test_upload_and_download_async(self, async_client: yadisk.AsyncClient, disk_root: str) -> None:
        if platform.system() == "Windows" and sys.version_info < (3, 12):
            pytest.skip("won't work on Windows with Python < 3.12")
            return

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
