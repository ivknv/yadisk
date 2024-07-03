# -*- coding: utf-8 -*-

import os
import tempfile

import posixpath
from unittest import TestCase
from io import BytesIO
from typing import Any

import yadisk

from yadisk._common import is_operation_link, ensure_path_has_schema
from yadisk._typing_compat import Callable
from yadisk._api import GetOperationStatusRequest
from yadisk.types import SessionName

from .test_session import TestSession
from .disk_gateway import DiskGateway, DiskGatewayClient
import threading

import asyncio
import time

__all__ = ["RequestsTestCase", "HTTPXTestCase", "PycURLTestCase"]


class BackgroundGatewayThread:
    def __init__(self, host: str, port: int):
        self.disk_gateway = DiskGateway()

        self.client = DiskGatewayClient(f"http://{host}:{port}")

        self.server_thread = threading.Thread(
            target=asyncio.run,
            args=(self.disk_gateway.run(host, port),)
        )

    def start(self):
        self.server_thread.start()

        while not self.client.is_running():
            time.sleep(0.01)

    def stop(self):
        self.disk_gateway.stop()
        self.client.close()
        self.server_thread.join()


def make_test_case(name: str, session_name: SessionName):
    class ClientTestCase(TestCase):
        client: yadisk.Client
        path: str
        gateway: BackgroundGatewayThread
        recording_enabled: bool
        replay_enabled: bool

        def record_or_replay(func: Callable):
            def decorated_test(self):
                directory = os.path.join("tests", "recorded", "sync")

                if self.recording_enabled:
                    os.makedirs(directory, exist_ok=True)

                    with self.gateway.client.record_as(os.path.join(directory, f"{func.__name__}.json")):
                        func(self)
                elif self.replay_enabled:
                    with self.gateway.client.replay(os.path.join(directory, f"{func.__name__}.json")):
                        func(self)
                else:
                    func(self)

            return decorated_test

        @classmethod
        def setUpClass(cls) -> None:
            gateway_host = os.environ.get("PYTHON_YADISK_GATEWAY_HOST", "0.0.0.0")
            gateway_port = int(os.environ.get("PYTHON_YADISK_GATEWAY_HOST", "8080"))

            cls.replay_enabled = os.environ.get("PYTHON_YADISK_REPLAY_ENABLED", "0") == "1"
            cls.recording_enabled = os.environ.get("PYTHON_YADISK_RECORDING_ENABLED", "0") == "1"

            base_gateway_url = f"http://{gateway_host}:{gateway_port}"

            cls.gateway = BackgroundGatewayThread(gateway_host, gateway_port)
            cls.gateway.start()

            if not os.environ.get("PYTHON_YADISK_APP_TOKEN"):
                raise ValueError("Environment variable PYTHON_YADISK_APP_TOKEN must be set")

            if not os.environ.get("PYTHON_YADISK_TEST_ROOT"):
                raise ValueError("Environment variable PYTHON_YADISK_TEST_ROOT must be set")

            if cls.replay_enabled:
                test_session = TestSession(
                    yadisk.import_session(session_name)(),
                    disk_base_url=f"{base_gateway_url}/replay/response/disk",
                    auth_base_url=f"{base_gateway_url}/replay/response/auth",
                    download_base_url=f"{base_gateway_url}/replay/response/download",
                    upload_base_url=f"{base_gateway_url}/replay/response/upload"
                )
            else:
                test_session = TestSession(
                    yadisk.import_session(session_name)(),
                    disk_base_url=f"{base_gateway_url}/forward/disk",
                    auth_base_url=f"{base_gateway_url}/forward/auth",
                    download_base_url=f"{base_gateway_url}/forward/download",
                    upload_base_url=f"{base_gateway_url}/forward/upload"
                )

            cls.client = yadisk.Client(
                os.environ["PYTHON_YADISK_APP_ID"],
                os.environ["PYTHON_YADISK_APP_SECRET"],
                os.environ["PYTHON_YADISK_APP_TOKEN"],
                session=test_session
            )

            cls.client.default_args.update({"n_retries": 50})

            cls.path = os.environ["PYTHON_YADISK_TEST_ROOT"]

            # Get rid of 'disk:/' prefix in the path and make it start with a slash
            # for consistency
            if cls.path.startswith("disk:/"):
                cls.path = posixpath.join("/", cls.path[len("disk:/"):])

            # Make sure the actual API token won't be exposed in the recorded requests
            cls.gateway.client.update_token_map({cls.client.token: "supposedly_valid_token"})

        @classmethod
        def tearDownClass(cls) -> None:
            cls.gateway.stop()
            cls.client.close()

        @record_or_replay
        def test_get_meta(self) -> None:
            resource = self.client.get_meta(self.path)

            self.assertIsInstance(resource, yadisk.objects.ResourceObject)
            self.assertEqual(resource.type, "dir")
            self.assertEqual(resource.name, posixpath.split(self.path)[1])

        @record_or_replay
        def test_listdir(self) -> None:
            names = ["dir1", "dir2", "dir3"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)

            result = [i.name for i in self.client.listdir(self.path)]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.remove(path, permanently=True)

            self.assertEqual(result, names)

        @record_or_replay
        def test_listdir_fields(self) -> None:
            names = ["dir1", "dir2", "dir3"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)

            result = [(i.name, i.type, i.file) for i in self.client.listdir(self.path, fields=["name", "type"])]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.remove(path, permanently=True)

            self.assertEqual(result, [(name, "dir", None) for name in names])

        @record_or_replay
        def test_listdir_on_file(self) -> None:
            buf = BytesIO()
            buf.write(b"0" * 1000)
            buf.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            self.client.upload(buf, path)

            with self.assertRaises(yadisk.exceptions.WrongResourceTypeError):
                list(self.client.listdir(path))

            self.client.remove(path, permanently=True)

        @record_or_replay
        def test_listdir_with_limits(self) -> None:
            names = ["dir1", "dir2", "dir3"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)

            result = [i.name for i in self.client.listdir(self.path, limit=1)]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.remove(path, permanently=True)

            self.assertEqual(result, names)

        @record_or_replay
        def test_listdir_with_max_items(self) -> None:
            names = ["dir1", "dir2", "dir3", "dir4", "dir5", "dir6"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)

            results = [
                [i.name for i in self.client.listdir(self.path, max_items=0)],
                [i.name for i in self.client.listdir(self.path, max_items=1, limit=1)],
                [i.name for i in self.client.listdir(self.path, max_items=2, limit=1)],
                [i.name for i in self.client.listdir(self.path, max_items=3, limit=1)],
                [i.name for i in self.client.listdir(self.path, max_items=10, limit=1)],
            ]

            expected = [
                [],
                names[:1],
                names[:2],
                names[:3],
                names[:10],
            ]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.remove(path, permanently=True)

            self.assertEqual(results, expected)

        @record_or_replay
        def test_mkdir_and_exists(self) -> None:
            names = ["dir1", "dir2"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)
                self.assertTrue(self.client.exists(path))

                self.client.remove(path, permanently=True)
                self.assertFalse(self.client.exists(path))

        @record_or_replay
        def test_upload_and_download(self) -> None:
            buf1 = BytesIO()
            buf2 = tempfile.NamedTemporaryFile("w+b")

            buf1.write(b"0" * 1024**2)
            buf1.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            self.client.upload(buf1, path, overwrite=True, n_retries=50)
            self.client.download(path, buf2.name, n_retries=50)
            self.client.remove(path, permanently=True)

            buf1.seek(0)
            buf2.seek(0)

            self.assertEqual(buf1.read(), buf2.read())

        @record_or_replay
        def test_check_token(self) -> None:
            self.assertTrue(self.client.check_token())
            self.assertFalse(self.client.check_token("asdasdasd"))

        @record_or_replay
        def test_permanent_remove(self) -> None:
            path = posixpath.join(self.path, "dir")
            origin_path = "disk:" + path

            self.client.mkdir(path)
            self.client.remove(path, permanently=True)

            for i in self.client.trash_listdir("/"):
                self.assertFalse(i.origin_path == origin_path)

        @record_or_replay
        def test_restore_trash(self) -> None:
            path = posixpath.join(self.path, "dir")
            origin_path = "disk:" + path

            self.client.mkdir(path)
            self.client.remove(path)

            trash_path: Any = None

            for i in self.client.trash_listdir("/"):
                if i.origin_path == origin_path:
                    trash_path = i.path
                    break

            self.assertTrue(trash_path is not None)

            self.client.restore_trash(trash_path, path)
            self.assertTrue(self.client.exists(path))
            self.client.remove(path, permanently=True)

        @record_or_replay
        def test_move(self) -> None:
            path1 = posixpath.join(self.path, "dir1")
            path2 = posixpath.join(self.path, "dir2")
            self.client.mkdir(path1)
            self.client.move(path1, path2)

            self.assertTrue(self.client.exists(path2))

            self.client.remove(path2, permanently=True)

        @record_or_replay
        def test_remove_trash(self) -> None:
            path = posixpath.join(self.path, "dir-to-remove")
            origin_path = "disk:" + path

            self.client.mkdir(path)
            self.client.remove(path)

            trash_path: Any = None

            for i in self.client.trash_listdir("/"):
                if i.origin_path == origin_path:
                    trash_path = i.path
                    break

            self.assertTrue(trash_path is not None)

            self.client.remove_trash(trash_path)
            self.assertFalse(self.client.trash_exists(trash_path))

        @record_or_replay
        def test_publish_unpublish(self) -> None:
            path = self.path

            self.client.publish(path)
            self.assertIsNotNone(self.client.get_meta(path).public_url)

            self.client.unpublish(path)
            self.assertIsNone(self.client.get_meta(path).public_url)

        @record_or_replay
        def test_patch(self) -> None:
            path = self.path

            self.client.patch(path, {"test_property": "I'm a value!"})

            props: Any = self.client.get_meta(path).custom_properties
            self.assertIsNotNone(props)

            self.assertEqual(props["test_property"], "I'm a value!")

            self.client.patch(path, {"test_property": None})
            self.assertIsNone(self.client.get_meta(path).custom_properties)

        @record_or_replay
        def test_issue7(self) -> None:
            # See https://github.com/ivknv/yadisk/issues/7

            try:
                list(self.client.public_listdir("any value here", path="any value here"))
            except yadisk.exceptions.PathNotFoundError:
                pass

        def test_is_operation_link(self) -> None:
            self.assertTrue(is_operation_link("https://cloud-api.yandex.net/v1/disk/operations/123asd"))
            self.assertTrue(is_operation_link("http://cloud-api.yandex.net/v1/disk/operations/123asd"))
            self.assertFalse(is_operation_link("https://cloud-api.yandex.net/v1/disk/operation/1283718"))
            self.assertFalse(is_operation_link("https://asd8iaysd89asdgiu"))
            self.assertFalse(is_operation_link("http://asd8iaysd89asdgiu"))

        def test_get_operation_status_request_url(self) -> None:
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

        def test_ensure_path_has_schema(self) -> None:
            # See https://github.com/ivknv/yadisk/issues/26 for more details

            self.assertEqual(ensure_path_has_schema("disk:"), "disk:/disk:")
            self.assertEqual(ensure_path_has_schema("trash:", default_schema="trash"), "trash:/trash:")
            self.assertEqual(ensure_path_has_schema("/asd:123"), "disk:/asd:123")
            self.assertEqual(ensure_path_has_schema("/asd:123", "trash"), "trash:/asd:123")
            self.assertEqual(ensure_path_has_schema("example/path"), "disk:/example/path")
            self.assertEqual(ensure_path_has_schema("app:/test"), "app:/test")

        @record_or_replay
        def test_upload_download_non_seekable(self) -> None:
            # It should be possible to upload/download non-seekable file objects (such as sys.stdin/sys.stdout)
            # See https://github.com/ivknv/yadisk/pull/31 for more details

            test_input_file = BytesIO(b"0" * 1000)
            test_input_file.seekable = lambda: False  # type: ignore

            def seek(*args, **kwargs):
                raise NotImplementedError

            test_input_file.seek = seek  # type: ignore

            dst_path = posixpath.join(self.path, "zeroes.txt")

            self.client.upload(test_input_file, dst_path, n_retries=50)

            test_output_file = BytesIO()
            test_output_file.seekable = lambda: False  # type: ignore
            test_output_file.seek = seek  # type: ignore

            self.client.download(dst_path, test_output_file, n_retries=50)

            self.client.remove(dst_path, permanently=True)

            self.assertEqual(test_input_file.tell(), 1000)
            self.assertEqual(test_output_file.tell(), 1000)

        @record_or_replay
        def test_upload_generator(self) -> None:
            data = b"0" * 1000

            def payload():
                yield data[:500]
                yield data[500:]

            dst_path = posixpath.join(self.path, "zeroes.txt")

            output = BytesIO()

            self.client.upload(payload, dst_path).download(output).remove(permanently=True)

            output.seek(0)

            self.assertEqual(output.read(), data)

    ClientTestCase.__name__ = name
    ClientTestCase.__qualname__ = ClientTestCase.__qualname__.rpartition(".")[0] + "." + name

    return ClientTestCase


RequestsTestCase = make_test_case("RequestsTestCase", "requests")
HTTPXTestCase = make_test_case("HTTPXTestCase", "httpx")
PycURLTestCase = make_test_case("PycURLTestCase", "pycurl")
