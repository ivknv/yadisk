# -*- coding: utf-8 -*-

import asyncio
import os
import tempfile
from typing import Any
import aiofiles

import posixpath
from unittest import IsolatedAsyncioTestCase
from io import BytesIO

import yadisk
from yadisk._common import is_operation_link, ensure_path_has_schema
from yadisk._typing_compat import Callable
from yadisk._api import GetOperationStatusRequest
from yadisk.types import AsyncSessionName

from .disk_gateway import DiskGateway, AsyncDiskGatewayClient
from .test_session import AsyncTestSession

__all__ = ["AIOHTTPTestCase", "AsyncHTTPXTestCase"]


class BackgroundGatewayTask:
    def __init__(self, host: str, port: int):
        self.disk_gateway = DiskGateway()

        self.client = AsyncDiskGatewayClient(f"http://{host}:{port}")
        self.host = host
        self.port = port
        self.server_task = None

    async def start(self):
        self.server_task = asyncio.create_task(self.disk_gateway.run(self.host, self.port))

        while not await self.client.is_running():
            await asyncio.sleep(0.01)

    async def stop(self):
        self.disk_gateway.stop()
        await self.client.close()

        if self.server_task is not None:
            await self.server_task


def make_test_case(name: str, session_name: AsyncSessionName):
    class AsyncClientTestCase(IsolatedAsyncioTestCase):
        client: yadisk.AsyncClient
        path: str
        gateway: BackgroundGatewayTask
        recording_enabled: bool
        replay_enabled: bool

        def record_or_replay(func: Callable):
            async def decorated_test(self):
                directory = os.path.join("tests", "recorded", "async", self.__class__.__name__)

                if self.recording_enabled:
                    os.makedirs(directory, exist_ok=True)

                    async with self.gateway.client.record_as(os.path.join(directory, f"{func.__name__}.json")):
                        await func(self)
                elif self.replay_enabled:
                    async with self.gateway.client.replay(os.path.join(directory, f"{func.__name__}.json")):
                        await func(self)
                else:
                    await func(self)

            return decorated_test

        async def asyncSetUp(self) -> None:
            gateway_host = os.environ.get("PYTHON_YADISK_GATEWAY_HOST", "0.0.0.0")
            gateway_port = int(os.environ.get("PYTHON_YADISK_GATEWAY_HOST", "8080"))

            self.replay_enabled = os.environ.get("PYTHON_YADISK_REPLAY_ENABLED", "0") == "1"
            self.recording_enabled = os.environ.get("PYTHON_YADISK_RECORDING_ENABLED", "0") == "1"

            base_gateway_url = f"http://{gateway_host}:{gateway_port}"

            self.gateway = BackgroundGatewayTask(gateway_host, gateway_port)
            await self.gateway.start()

            if not os.environ.get("PYTHON_YADISK_APP_TOKEN"):
                raise ValueError("Environment variable PYTHON_YADISK_APP_TOKEN must be set")

            if not os.environ.get("PYTHON_YADISK_TEST_ROOT"):
                raise ValueError("Environment variable PYTHON_YADISK_TEST_ROOT must be set")

            self.path: str = os.environ["PYTHON_YADISK_TEST_ROOT"]

            # Get rid of 'disk:/' prefix in the path and make it start with a slash
            # for consistency
            if self.path.startswith("disk:/"):
                self.path = posixpath.join("/", self.path[len("disk:/"):])

            if self.replay_enabled:
                test_session = AsyncTestSession(
                    yadisk.import_async_session(session_name)(),
                    disk_base_url=f"{base_gateway_url}/replay/response/disk",
                    auth_base_url=f"{base_gateway_url}/replay/response/auth",
                    download_base_url=f"{base_gateway_url}/replay/response/download",
                    upload_base_url=f"{base_gateway_url}/replay/response/upload"
                )
            else:
                test_session = AsyncTestSession(
                    yadisk.import_async_session(session_name)(),
                    disk_base_url=f"{base_gateway_url}/forward/disk",
                    auth_base_url=f"{base_gateway_url}/forward/auth",
                    download_base_url=f"{base_gateway_url}/forward/download",
                    upload_base_url=f"{base_gateway_url}/forward/upload"
                )

            self.client = yadisk.AsyncClient(
                os.environ.get("PYTHON_YADISK_APP_ID", ""),
                os.environ.get("PYTHON_YADISK_APP_SECRET", ""),
                os.environ["PYTHON_YADISK_APP_TOKEN"],
                session=test_session
            )

            self.client.default_args.update({"n_retries": 50})

            # Make sure the actual API token won't be exposed in the recorded requests
            await self.gateway.client.update_token_map({self.client.token: "supposedly_valid_token"})

        async def asyncTearDown(self) -> None:
            await self.client.close()
            await self.gateway.stop()

            if session_name == "aiohttp":
                # Needed for aiohttp to correctly release its resources (see https://github.com/aio-libs/aiohttp/issues/1115)
                await asyncio.sleep(0.1)

        @record_or_replay
        async def test_get_meta(self) -> None:
            resource = await self.client.get_meta(self.path)

            self.assertIsInstance(resource, yadisk.objects.ResourceObject)
            self.assertEqual(resource.type, "dir")
            self.assertEqual(resource.name, posixpath.split(self.path)[1])

        @record_or_replay
        async def test_listdir(self) -> None:
            names = ["dir1", "dir2", "dir3"]
            paths = [posixpath.join(self.path, name) for name in names]

            for path in paths:
                await self.client.mkdir(path)

            async def get_result():
                return [i.name async for i in self.client.listdir(self.path)]

            result = await get_result()

            for path in paths:
                await self.client.remove(path, permanently=True)

            self.assertEqual(result, names)

        @record_or_replay
        async def test_listdir_fields(self) -> None:
            names = ["dir1", "dir2", "dir3"]
            paths = [posixpath.join(self.path, name) for name in names]

            for path in paths:
                await self.client.mkdir(path)

            async def get_result():
                return [(i.name, i.type, i.file)
                        async for i in self.client.listdir(self.path, fields=["name", "type"])]

            result = await get_result()

            for path in paths:
                await self.client.remove(path, permanently=True)

            self.assertEqual(result, [(name, "dir", None) for name in names])

        @record_or_replay
        async def test_listdir_on_file(self) -> None:
            buf = BytesIO()
            buf.write(b"0" * 1000)
            buf.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            await self.client.upload(buf, path)

            with self.assertRaises(yadisk.exceptions.WrongResourceTypeError):
                [i async for i in self.client.listdir(path)]

            await self.client.remove(path, permanently=True)

        @record_or_replay
        async def test_listdir_with_limits(self) -> None:
            names = ["dir1", "dir2", "dir3"]
            paths = [posixpath.join(self.path, name) for name in names]

            for path in paths:
                await self.client.mkdir(path)

            async def get_result():
                return [i.name async for i in self.client.listdir(self.path, limit=1)]

            result = await get_result()

            for path in paths:
                await self.client.remove(path, permanently=True)

            self.assertEqual(result, names)

        @record_or_replay
        async def test_mkdir_and_exists(self) -> None:
            names = ["dir1", "dir2", "dir3"]
            paths = [posixpath.join(self.path, name) for name in names]

            async def check_existence(path):
                await self.client.mkdir(path)
                self.assertTrue(await self.client.exists(path))

                await self.client.remove(path, permanently=True)
                self.assertFalse(await self.client.exists(path))

            for path in paths:
                await check_existence(path)

        @record_or_replay
        async def test_upload_and_download(self) -> None:
            buf1 = BytesIO()
            buf2 = tempfile.NamedTemporaryFile("w+b")

            def wrapper():
                self.assertTrue(False)

            buf1.close = wrapper  # type: ignore

            buf1.write(b"0" * 1024**2)
            buf1.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            await self.client.upload(buf1, path, overwrite=True, n_retries=50)
            await self.client.download(path, buf2.name, n_retries=50)
            await self.client.remove(path, permanently=True)

            buf1.seek(0)
            buf2.seek(0)

            self.assertEqual(buf1.read(), buf2.read())

        @record_or_replay
        async def test_upload_and_download_async(self) -> None:
            content = b"0" * 1024 ** 2
            async with aiofiles.tempfile.NamedTemporaryFile("wb+") as source:
                await source.write(content)
                await source.seek(0)

                path1 = posixpath.join(self.path, "zeroes.txt")
                path2 = posixpath.join(self.path, "zeroes_from_generator.txt")

                await self.client.upload(source, path1, overwrite=True, n_retries=50)

                async def source_generator():
                    for _ in range(1024):
                        yield b"0" * 1024

                await self.client.upload(source_generator, path2, overwrite=True, n_retries=50)

            async with aiofiles.tempfile.NamedTemporaryFile("wb+") as destination:
                await self.client.download(path1, destination, n_retries=50)
                await destination.seek(0)

                self.assertEqual(content, await destination.read())
                await self.client.remove(path1, permanently=True)

                await destination.seek(0)
                await destination.truncate()
                await self.client.download(path2, destination, n_retries=50)
                await destination.seek(0)

                self.assertEqual(content, await destination.read())
                await self.client.remove(path2, permanently=True)

        @record_or_replay
        async def test_check_token(self) -> None:
            self.assertTrue(await self.client.check_token())
            self.assertFalse(await self.client.check_token("asdasdasd"))

        @record_or_replay
        async def test_permanent_remove(self) -> None:
            path = posixpath.join(self.path, "dir")
            origin_path = "disk:" + path

            await self.client.mkdir(path)
            await self.client.remove(path, permanently=True)

            async for i in self.client.trash_listdir("/"):
                self.assertFalse(i.origin_path == origin_path)

        @record_or_replay
        async def test_restore_trash(self) -> None:
            path = posixpath.join(self.path, "dir")
            origin_path = "disk:" + path

            await self.client.mkdir(path)
            await self.client.remove(path)

            trash_path: Any = None

            async for i in self.client.trash_listdir("/"):
                if i.origin_path == origin_path:
                    trash_path = i.path
                    break

            self.assertTrue(trash_path is not None)

            await self.client.restore_trash(trash_path, path)
            self.assertTrue(await self.client.exists(path))
            await self.client.remove(path, permanently=True)

        @record_or_replay
        async def test_move(self) -> None:
            path1 = posixpath.join(self.path, "dir1")
            path2 = posixpath.join(self.path, "dir2")
            await self.client.mkdir(path1)
            await self.client.move(path1, path2)

            self.assertTrue(await self.client.exists(path2))

            await self.client.remove(path2, permanently=True)

        @record_or_replay
        async def test_remove_trash(self) -> None:
            path = posixpath.join(self.path, "dir-to-remove")
            origin_path = "disk:" + path

            await self.client.mkdir(path)
            await self.client.remove(path)

            trash_path: Any = None

            async for i in self.client.trash_listdir("/"):
                if i.origin_path == origin_path:
                    trash_path = i.path
                    break

            self.assertTrue(trash_path is not None)

            await self.client.remove_trash(trash_path)
            self.assertFalse(await self.client.trash_exists(trash_path))

        @record_or_replay
        async def test_publish_unpublish(self) -> None:
            path = self.path

            await self.client.publish(path)
            self.assertIsNotNone((await self.client.get_meta(path)).public_url)

            await self.client.unpublish(path)
            self.assertIsNone((await self.client.get_meta(path)).public_url)

        @record_or_replay
        async def test_patch(self) -> None:
            path = self.path

            await self.client.patch(path, {"test_property": "I'm a value!"})

            props: Any = (await self.client.get_meta(path)).custom_properties
            self.assertIsNotNone(props)
            self.assertEqual(props["test_property"], "I'm a value!")

            await self.client.patch(path, {"test_property": None})
            self.assertIsNone((await self.client.get_meta(path)).custom_properties)

        @record_or_replay
        async def test_issue7(self) -> None:
            # See https://github.com/ivknv/yadisk/issues/7

            try:
                [i async for i in self.client.public_listdir("any value here", path="any value here")]
            except yadisk.exceptions.PathNotFoundError:
                pass

        def test_is_operation_link(self) -> None:
            self.assertTrue(is_operation_link("https://cloud-api.yandex.net/v1/disk/operations/123asd"))
            self.assertTrue(is_operation_link("http://cloud-api.yandex.net/v1/disk/operations/123asd"))
            self.assertFalse(is_operation_link("https://cloud-api.yandex.net/v1/disk/operation/1283718"))
            self.assertFalse(is_operation_link("https://asd8iaysd89asdgiu"))
            self.assertFalse(is_operation_link("http://asd8iaysd89asdgiu"))

        @record_or_replay
        async def test_get_operation_status_request_url(self) -> None:
            request = GetOperationStatusRequest(
                self.client.session,
                "https://cloud-api.yandex.net/v1/disk/operations/123asd")
            self.assertTrue(is_operation_link(request.url))

            request = GetOperationStatusRequest(
                self.client.session,
                "http://cloud-api.yandex.net/v1/disk/operations/123asd")
            self.assertTrue(is_operation_link(request.url))
            self.assertTrue(request.url.startswith("https://"))

            request = GetOperationStatusRequest(
                self.client.session,
                "https://asd8iaysd89asdgiu")
            self.assertTrue(is_operation_link(request.url))
            self.assertTrue(request.url.startswith("https://"))

        @record_or_replay
        async def test_is_file(self) -> None:
            # See https://github.com/ivknv/yadisk-async/pull/6
            buf1 = BytesIO()

            buf1.write(b"0" * 1024**2)
            buf1.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            await self.client.upload(buf1, path, overwrite=True, n_retries=50)
            self.assertTrue(await self.client.is_file(path))
            await self.client.remove(path, permanently=True)

        def test_ensure_path_has_schema(self) -> None:
            # See https://github.com/ivknv/yadisk/issues/26 for more details

            self.assertEqual(ensure_path_has_schema("disk:"), "disk:/disk:")
            self.assertEqual(ensure_path_has_schema("trash:", default_schema="trash"), "trash:/trash:")
            self.assertEqual(ensure_path_has_schema("/asd:123"), "disk:/asd:123")
            self.assertEqual(ensure_path_has_schema("/asd:123", "trash"), "trash:/asd:123")
            self.assertEqual(ensure_path_has_schema("example/path"), "disk:/example/path")
            self.assertEqual(ensure_path_has_schema("app:/test"), "app:/test")

        @record_or_replay
        async def test_upload_download_non_seekable(self) -> None:
            # It should be possible to upload/download non-seekable file objects (such as stdin/stdout)
            # See https://github.com/ivknv/yadisk/pull/31 for more details

            test_input_file = BytesIO(b"0" * 1000)
            test_input_file.seekable = lambda: False  # type: ignore

            def seek(*args, **kwargs):
                raise NotImplementedError

            test_input_file.seek = seek  # type: ignore

            dst_path = posixpath.join(self.path, "zeroes.txt")

            await self.client.upload(test_input_file, dst_path, n_retries=50)

            test_output_file = BytesIO()
            test_output_file.seekable = lambda: False  # type: ignore
            test_output_file.seek = seek  # type: ignore

            await self.client.download(dst_path, test_output_file, n_retries=50)

            await self.client.remove(dst_path, permanently=True)

            self.assertEqual(test_input_file.tell(), 1000)
            self.assertEqual(test_output_file.tell(), 1000)

    AsyncClientTestCase.__name__ = name
    AsyncClientTestCase.__qualname__ = AsyncClientTestCase.__qualname__.rpartition(".")[0] + "." + name

    return AsyncClientTestCase


AIOHTTPTestCase = make_test_case("AIOHTTPTestCase", "aiohttp")
AsyncHTTPXTestCase = make_test_case("AsyncHTTPXTestCase", "httpx")
