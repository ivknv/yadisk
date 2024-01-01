# -*- coding: utf-8 -*-

import os
import tempfile

import posixpath
from unittest import TestCase
from io import BytesIO
from typing import Any

import yadisk
from yadisk.sessions.requests_session import RequestsSession
from yadisk.sessions.httpx_session import HTTPXSession
from yadisk.sessions.pycurl_session import PycURLSession

from yadisk.common import is_operation_link, ensure_path_has_schema
from yadisk.api.operations import GetOperationStatusRequest

__all__ = ["RequestsTestCase", "HTTPXTestCase", "PycURLTestCase"]

def make_test_case(name: str, session: yadisk.Session):
    class ClientTestCase(TestCase):
        client: yadisk.Client
        path: str

        @classmethod
        def setUpClass(cls):
            if not os.environ.get("PYTHON_YADISK_APP_TOKEN"):
                raise ValueError("Environment variable PYTHON_YADISK_APP_TOKEN must be set")

            if not os.environ.get("PYTHON_YADISK_TEST_ROOT"):
                raise ValueError("Environment variable PYTHON_YADISK_TEST_ROOT must be set")

            cls.client = yadisk.Client(os.environ["PYTHON_YADISK_APP_ID"],
                                       os.environ["PYTHON_YADISK_APP_SECRET"],
                                       os.environ["PYTHON_YADISK_APP_TOKEN"],
                                       session=session)
            cls.client.default_args["n_retries"] = 50

            cls.path = os.environ["PYTHON_YADISK_TEST_ROOT"]

            # Get rid of 'disk:/' prefix in the path and make it start with a slash
            # for consistency
            if cls.path.startswith("disk:/"):
                cls.path = posixpath.join("/", cls.path[len("disk:/"):])

        @classmethod
        def tearDownClass(cls):
            cls.client.close()

        def test_get_meta(self):
            resource = self.client.get_meta(self.path)

            self.assertIsInstance(resource, yadisk.objects.ResourceObject)
            self.assertEqual(resource.type, "dir")
            self.assertEqual(resource.name, posixpath.split(self.path)[1])

        def test_listdir(self):
            names = ["dir1", "dir2", "dir3"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)

            result = [i.name for i in self.client.listdir(self.path)]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.remove(path, permanently=True)

            self.assertEqual(result, names)

        def test_listdir_fields(self):
            names = ["dir1", "dir2", "dir3"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)

            result = [(i.name, i.type, i.file) for i in self.client.listdir(self.path, fields=["name", "type"])]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.remove(path, permanently=True)

            self.assertEqual(result, [(name, "dir", None) for name in names])

        def test_listdir_on_file(self):
            buf = BytesIO()
            buf.write(b"0" * 1000)
            buf.seek(0)

            path = posixpath.join(self.path, "zeroes.txt")

            self.client.upload(buf, path)

            with self.assertRaises(yadisk.exceptions.WrongResourceTypeError):
                list(self.client.listdir(path))

            self.client.remove(path, permanently=True)

        def test_listdir_with_limits(self):
            names = ["dir1", "dir2", "dir3"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)

            result = [i.name for i in self.client.listdir(self.path, limit=1)]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.remove(path, permanently=True)

            self.assertEqual(result, names)

        def test_mkdir_and_exists(self):
            names = ["dir1", "dir2"]

            for name in names:
                path = posixpath.join(self.path, name)

                self.client.mkdir(path)
                self.assertTrue(self.client.exists(path))

                self.client.remove(path, permanently=True)
                self.assertFalse(self.client.exists(path))

        def test_upload_and_download(self):
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

        def test_check_token(self):
            self.assertTrue(self.client.check_token())
            self.assertFalse(self.client.check_token("asdasdasd"))

        def test_permanent_remove(self):
            path = posixpath.join(self.path, "dir")
            origin_path = "disk:" + path

            self.client.mkdir(path)
            self.client.remove(path, permanently=True)

            for i in self.client.trash_listdir("/"):
                self.assertFalse(i.origin_path == origin_path)

        def test_restore_trash(self):
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

        def test_move(self):
            path1 = posixpath.join(self.path, "dir1")
            path2 = posixpath.join(self.path, "dir2")
            self.client.mkdir(path1)
            self.client.move(path1, path2)

            self.assertTrue(self.client.exists(path2))

            self.client.remove(path2, permanently=True)

        def test_remove_trash(self):
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

        def test_publish_unpublish(self):
            path = self.path

            self.client.publish(path)
            self.assertIsNotNone(self.client.get_meta(path).public_url)

            self.client.unpublish(path)
            self.assertIsNone(self.client.get_meta(path).public_url)

        def test_patch(self):
            path = self.path

            self.client.patch(path, {"test_property": "I'm a value!"})

            props: Any = self.client.get_meta(path).custom_properties
            self.assertIsNotNone(props)

            self.assertEqual(props["test_property"], "I'm a value!")

            self.client.patch(path, {"test_property": None})
            self.assertIsNone(self.client.get_meta(path).custom_properties)

        def test_issue7(self):
            # See https://github.com/ivknv/yadisk/issues/7

            try:
                self.client.public_listdir("any value here", path="any value here")
            except yadisk.exceptions.PathNotFoundError:
                pass

        def test_is_operation_link(self):
            self.assertTrue(is_operation_link("https://cloud-api.yandex.net/v1/disk/operations/123asd"))
            self.assertTrue(is_operation_link("http://cloud-api.yandex.net/v1/disk/operations/123asd"))
            self.assertFalse(is_operation_link("https://cloud-api.yandex.net/v1/disk/operation/1283718"))
            self.assertFalse(is_operation_link("https://asd8iaysd89asdgiu"))
            self.assertFalse(is_operation_link("http://asd8iaysd89asdgiu"))

        def test_get_operation_status_request_url(self):
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

        def test_ensure_path_has_schema(self):
            # See https://github.com/ivknv/yadisk/issues/26 for more details

            self.assertEqual(ensure_path_has_schema("disk:"), "disk:/disk:")
            self.assertEqual(ensure_path_has_schema("trash:", default_schema="trash"), "trash:/trash:")
            self.assertEqual(ensure_path_has_schema("/asd:123"), "disk:/asd:123")
            self.assertEqual(ensure_path_has_schema("/asd:123", "trash"), "trash:/asd:123")
            self.assertEqual(ensure_path_has_schema("example/path"), "disk:/example/path")
            self.assertEqual(ensure_path_has_schema("app:/test"), "app:/test")

        def test_upload_download_non_seekable(self):
            # It should be possible to upload/download non-seekable file objects (such as sys.stdin/sys.stdout)
            # See https://github.com/ivknv/yadisk/pull/31 for more details

            test_input_file = BytesIO(b"0" * 1000)
            test_input_file.seekable = lambda: False

            def seek(*args, **kwargs):
                raise NotImplementedError

            test_input_file.seek = seek

            dst_path = posixpath.join(self.path, "zeroes.txt")

            self.client.upload(test_input_file, dst_path, n_retries=50)

            test_output_file = BytesIO()
            test_output_file.seekable = lambda: False
            test_output_file.seek = seek

            self.client.download(dst_path, test_output_file, n_retries=50)

            self.client.remove(dst_path, permanently=True)

            self.assertEqual(test_input_file.tell(), 1000)
            self.assertEqual(test_output_file.tell(), 1000)

        def test_upload_generator(self):
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

RequestsTestCase = make_test_case("RequestsTestCase", RequestsSession())
HTTPXTestCase = make_test_case("HTTPXTestCase", HTTPXSession())
PycURLTestCase = make_test_case("PycURLTestCase", PycURLSession())
