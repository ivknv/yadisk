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
from yadisk.common import is_operation_link, ensure_path_has_schema
from yadisk.api.operations import GetOperationStatusRequest
from yadisk.types import AsyncSessionName

__all__ = ["AIOHTTPTestCase", "AsyncHTTPXTestCase"]

def make_test_case(name: str, session: AsyncSessionName):
    class AsyncClientTestCase(IsolatedAsyncioTestCase):
        client: yadisk.AsyncClient
        path: str

        async def asyncSetUp(self):
            if not os.environ.get("PYTHON_YADISK_APP_TOKEN"):
                raise ValueError("Environment variable PYTHON_YADISK_APP_TOKEN must be set")

            if not os.environ.get("PYTHON_YADISK_TEST_ROOT"):
                raise ValueError("Environment variable PYTHON_YADISK_TEST_ROOT must be set")

            self.path: str = os.environ["PYTHON_YADISK_TEST_ROOT"]

            # Get rid of 'disk:/' prefix in the path and make it start with a slash
            # for consistency
            if self.path.startswith("disk:/"):
                self.path = posixpath.join("/", self.path[len("disk:/"):])

            self.client: yadisk.AsyncClient = yadisk.AsyncClient(
                os.environ.get("PYTHON_YADISK_APP_ID", ""),
                os.environ.get("PYTHON_YADISK_APP_SECRET", ""),
                os.environ["PYTHON_YADISK_APP_TOKEN"],
                session=session)
            self.client.default_args["n_retries"] = 50

        async def asyncTearDown(self):
            await self.client.close()

            if session == "aiohttp":
                # Needed for aiohttp to correctly release its resources (see https://github.com/aio-libs/aiohttp/issues/1115)
                await asyncio.sleep(0.1)

        async def test_get_meta(self):
            resource = await self.client.get_meta(self.path)

            self.assertIsInstance(resource, yadisk.objects.ResourceObject)
            self.assertEqual(resource.type, "dir")
            self.assertEqual(resource.name, posixpath.split(self.path)[1])

        async def test_listdir(self):
            names = ["dir1", "dir2", "dir3"]
            paths = [posixpath.join(self.path, name) for name in names]
            mkdir_tasks = [self.client.mkdir(path) for path in paths]

            await asyncio.gather(*mkdir_tasks)

            async def get_result():
                return [i.name async for i in await self.client.listdir(self.path)]

            result = await get_result()

            remove_tasks = [self.client.remove(path, permanently=True) for path in paths]

            await asyncio.gather(*remove_tasks)

            self.assertEqual(result, names)

        async def test_listdir_fields(self):
            names = ["dir1", "dir2", "dir3"]
            paths = [posixpath.join(self.path, name) for name in names]
            mkdir_tasks = [self.client.mkdir(path) for path in paths]

            await asyncio.gather(*mkdir_tasks)

            async def get_result():
                return [(i.name, i.type, i.file)
                        async for i in await self.client.listdir(self.path, fields=["name", "type"])]

            result = await get_result()

            remove_tasks = [self.client.remove(path, permanently=True) for path in paths]

            await asyncio.gather(*remove_tasks)

            self.assertEqual(result, [(name, "dir", None) for name in names])

        async def test_listdir_on_file(self):
            buf = BytesIO()
            buf.write(b"0" * 1000)
            buf.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            await self.client.upload(buf, path)

            with self.assertRaises(yadisk.exceptions.WrongResourceTypeError):
                [i async for i in await self.client.listdir(path)]

            await self.client.remove(path, permanently=True)

        async def test_listdir_with_limits(self):
            names = ["dir1", "dir2", "dir3"]
            paths = [posixpath.join(self.path, name) for name in names]
            mkdir_tasks = [self.client.mkdir(path) for path in paths]

            await asyncio.gather(*mkdir_tasks)

            async def get_result():
                return [i.name async for i in await self.client.listdir(self.path, limit=1)]

            result = await get_result()

            remove_tasks = [self.client.remove(path, permanently=True) for path in paths]

            await asyncio.gather(*remove_tasks)

            self.assertEqual(result, names)

        async def test_mkdir_and_exists(self):
            names = ["dir1", "dir2", "dir3"]
            paths = [posixpath.join(self.path, name) for name in names]

            async def check_existence(path):
                await self.client.mkdir(path)
                self.assertTrue(await self.client.exists(path))

                await self.client.remove(path, permanently=True)
                self.assertFalse(await self.client.exists(path))

            tasks = [check_existence(path) for path in paths]

            await asyncio.gather(*tasks)

        async def test_upload_and_download(self):
            buf1 = BytesIO()
            buf2 = tempfile.NamedTemporaryFile("w+b")

            def wrapper():
                self.assertTrue(False)

            buf1.close = wrapper

            buf1.write(b"0" * 1024**2)
            buf1.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            await self.client.upload(buf1, path, overwrite=True, n_retries=50)
            await self.client.download(path, buf2.name, n_retries=50)
            await self.client.remove(path, permanently=True)

            buf1.seek(0)
            buf2.seek(0)

            self.assertEqual(buf1.read(), buf2.read())

        async def test_upload_and_download_async(self):
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

        async def test_check_token(self):
            self.assertTrue(await self.client.check_token())
            self.assertFalse(await self.client.check_token("asdasdasd"))

        async def test_permanent_remove(self):
            path = posixpath.join(self.path, "dir")
            origin_path = "disk:" + path

            await self.client.mkdir(path)
            await self.client.remove(path, permanently=True)

            async for i in await self.client.trash_listdir("/"):
                self.assertFalse(i.origin_path == origin_path)

        async def test_restore_trash(self):
            path = posixpath.join(self.path, "dir")
            origin_path = "disk:" + path

            await self.client.mkdir(path)
            await self.client.remove(path)

            trash_path: Any = None

            async for i in await self.client.trash_listdir("/"):
                if i.origin_path == origin_path:
                    trash_path = i.path
                    break

            self.assertTrue(trash_path is not None)

            await self.client.restore_trash(trash_path, path)
            self.assertTrue(await self.client.exists(path))
            await self.client.remove(path, permanently=True)

        async def test_move(self):
            path1 = posixpath.join(self.path, "dir1")
            path2 = posixpath.join(self.path, "dir2")
            await self.client.mkdir(path1)
            await self.client.move(path1, path2)

            self.assertTrue(await self.client.exists(path2))

            await self.client.remove(path2, permanently=True)

        async def test_remove_trash(self):
            path = posixpath.join(self.path, "dir-to-remove")
            origin_path = "disk:" + path

            await self.client.mkdir(path)
            await self.client.remove(path)

            trash_path: Any = None

            async for i in await self.client.trash_listdir("/"):
                if i.origin_path == origin_path:
                    trash_path = i.path
                    break

            self.assertTrue(trash_path is not None)

            await self.client.remove_trash(trash_path)
            self.assertFalse(await self.client.trash_exists(trash_path))

        async def test_publish_unpublish(self):
            path = self.path

            await self.client.publish(path)
            self.assertIsNotNone((await self.client.get_meta(path)).public_url)

            await self.client.unpublish(path)
            self.assertIsNone((await self.client.get_meta(path)).public_url)

        async def test_patch(self):
            path = self.path

            await self.client.patch(path, {"test_property": "I'm a value!"})

            props: Any = (await self.client.get_meta(path)).custom_properties
            self.assertIsNotNone(props)
            self.assertEqual(props["test_property"], "I'm a value!")

            await self.client.patch(path, {"test_property": None})
            self.assertIsNone((await self.client.get_meta(path)).custom_properties)

        async def test_issue7(self):
            # See https://github.com/ivknv/yadisk/issues/7

            try:
                await self.client.public_listdir("any value here", path="any value here")
            except yadisk.exceptions.PathNotFoundError:
                pass

        def test_is_operation_link(self):
            self.assertTrue(is_operation_link("https://cloud-api.yandex.net/v1/disk/operations/123asd"))
            self.assertTrue(is_operation_link("http://cloud-api.yandex.net/v1/disk/operations/123asd"))
            self.assertFalse(is_operation_link("https://cloud-api.yandex.net/v1/disk/operation/1283718"))
            self.assertFalse(is_operation_link("https://asd8iaysd89asdgiu"))
            self.assertFalse(is_operation_link("http://asd8iaysd89asdgiu"))

        async def test_get_operation_status_request_url(self):
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

        async def test_is_file(self):
            # See https://github.com/ivknv/yadisk-async/pull/6
            buf1 = BytesIO()

            buf1.write(b"0" * 1024**2)
            buf1.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            await self.client.upload(buf1, path, overwrite=True, n_retries=50)
            self.assertTrue(await self.client.is_file(path))
            await self.client.remove(path, permanently=True)

        def test_ensure_path_has_schema(self):
            # See https://github.com/ivknv/yadisk/issues/26 for more details

            self.assertEqual(ensure_path_has_schema("disk:"), "disk:/disk:")
            self.assertEqual(ensure_path_has_schema("trash:", default_schema="trash"), "trash:/trash:")
            self.assertEqual(ensure_path_has_schema("/asd:123"), "disk:/asd:123")
            self.assertEqual(ensure_path_has_schema("/asd:123", "trash"), "trash:/asd:123")
            self.assertEqual(ensure_path_has_schema("example/path"), "disk:/example/path")
            self.assertEqual(ensure_path_has_schema("app:/test"), "app:/test")

        async def test_upload_download_non_seekable(self):
            # It should be possible to upload/download non-seekable file objects (such as stdin/stdout)
            # See https://github.com/ivknv/yadisk/pull/31 for more details

            test_input_file = BytesIO(b"0" * 1000)
            test_input_file.seekable = lambda: False

            def seek(*args, **kwargs):
                raise NotImplementedError

            test_input_file.seek = seek

            dst_path = posixpath.join(self.path, "zeroes.txt")

            await self.client.upload(test_input_file, dst_path, n_retries=50)

            test_output_file = BytesIO()
            test_output_file.seekable = lambda: False
            test_output_file.seek = seek

            await self.client.download(dst_path, test_output_file, n_retries=50)

            await self.client.remove(dst_path, permanently=True)

            self.assertEqual(test_input_file.tell(), 1000)
            self.assertEqual(test_output_file.tell(), 1000)

    AsyncClientTestCase.__name__ = name
    AsyncClientTestCase.__qualname__ = AsyncClientTestCase.__qualname__.rpartition(".")[0] + "." + name

    return AsyncClientTestCase

AIOHTTPTestCase = make_test_case("AIOHTTPTestCase", "aiohttp")
AsyncHTTPXTestCase = make_test_case("AsyncHTTPXTestCase", "httpx")
