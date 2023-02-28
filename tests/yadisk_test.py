#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

import posixpath
from unittest import TestCase
from io import BytesIO

import yadisk
from yadisk.common import is_operation_link, ensure_path_has_schema
from yadisk.api.operations import GetOperationStatusRequest

yadisk.settings.DEFAULT_N_RETRIES = 50

__all__ = ["YaDiskTestCase"]

class YaDiskTestCase(TestCase):
    def setUp(self):
        if not os.environ.get("PYTHON_YADISK_APP_TOKEN"):
            raise ValueError("Environment variable PYTHON_YADISK_APP_TOKEN must be set")

        if not os.environ.get("PYTHON_YADISK_TEST_ROOT"):
            raise ValueError("Environment variable PYTHON_YADISK_TEST_ROOT must be set")

        self.yadisk = yadisk.YaDisk(os.environ.get("PYTHON_YADISK_APP_ID"),
                                    os.environ.get("PYTHON_YADISK_APP_SECRET"),
                                    os.environ.get("PYTHON_YADISK_APP_TOKEN"))

        self.path = os.environ.get("PYTHON_YADISK_TEST_ROOT")

        # Get rid of 'disk:/' prefix in the path and make it start with a slash
        # for consistency
        if self.path.startswith("disk:/"):
            self.path = posixpath.join("/", self.path[len("disk:/"):])

    def test_get_meta(self):
       self.assertIsInstance(self.yadisk.get_meta(self.path), yadisk.objects.ResourceObject)

    def test_listdir(self):
        names = ["dir1", "dir2", "dir3"]

        for name in names:
            path = posixpath.join(self.path, name)

            self.yadisk.mkdir(path)

        result = [i.name for i in self.yadisk.listdir(self.path)]

        for name in names:
            path = posixpath.join(self.path, name)

            self.yadisk.remove(path, permanently=True)

        self.assertEqual(result, names)

    def test_listdir_fields(self):
        names = ["dir1", "dir2", "dir3"]

        for name in names:
            path = posixpath.join(self.path, name)

            self.yadisk.mkdir(path)

        result = [(i.name, i.type, i.file) for i in self.yadisk.listdir(self.path, fields=["name", "type"])]

        for name in names:
            path = posixpath.join(self.path, name)

            self.yadisk.remove(path, permanently=True)

        self.assertEqual(result, [(name, "dir", None) for name in names])

    def test_listdir_on_file(self):
        buf = BytesIO()
        buf.write(b"0" * 1000)
        buf.seek(0)

        path = posixpath.join(self.path, "zeroes.txt")

        self.yadisk.upload(buf, path)

        with self.assertRaises(yadisk.exceptions.WrongResourceTypeError):
            list(self.yadisk.listdir(path))

        self.yadisk.remove(path, permanently=True)

    def test_listdir_with_limits(self):
        names = ["dir1", "dir2", "dir3"]

        for name in names:
            path = posixpath.join(self.path, name)

            self.yadisk.mkdir(path)

        result = [i.name for i in self.yadisk.listdir(self.path, limit=1)]

        for name in names:
            path = posixpath.join(self.path, name)

            self.yadisk.remove(path, permanently=True)

        self.assertEqual(result, names)

    def test_mkdir_and_exists(self):
        names = ["dir1", "dir2"]

        for name in names:
            path = posixpath.join(self.path, name)

            self.yadisk.mkdir(path)
            self.assertTrue(self.yadisk.exists(path))

            self.yadisk.remove(path, permanently=True)
            self.assertFalse(self.yadisk.exists(path))

    def test_upload_and_download(self):
        buf1 = BytesIO()
        buf2 = tempfile.NamedTemporaryFile("w+b")

        buf1.write(b"0" * 1024**2)
        buf1.seek(0)

        path = posixpath.join(self.path, "zeroes.txt")

        self.yadisk.upload(buf1, path, overwrite=True, n_retries=50)
        self.yadisk.download(path, buf2.name, n_retries=50)
        self.yadisk.remove(path, permanently=True)

        buf1.seek(0)
        buf2.seek(0)

        self.assertEqual(buf1.read(), buf2.read())

    def test_check_token(self):
        self.assertTrue(self.yadisk.check_token())
        self.assertFalse(self.yadisk.check_token("asdasdasd"))

    def test_permanent_remove(self):
        path = posixpath.join(self.path, "dir")
        origin_path = "disk:" + path

        self.yadisk.mkdir(path)
        self.yadisk.remove(path, permanently=True)

        for i in self.yadisk.trash_listdir("/"):
            self.assertFalse(i.origin_path == origin_path)

    def test_restore_trash(self):
        path = posixpath.join(self.path, "dir")
        origin_path = "disk:" + path

        self.yadisk.mkdir(path)
        self.yadisk.remove(path)

        trash_path = None

        for i in self.yadisk.trash_listdir("/"):
            if i.origin_path == origin_path:
                trash_path = i.path
                break

        self.assertTrue(trash_path is not None)

        self.yadisk.restore_trash(trash_path, path)
        self.assertTrue(self.yadisk.exists(path))
        self.yadisk.remove(path, permanently=True)

    def test_move(self):
        path1 = posixpath.join(self.path, "dir1")
        path2 = posixpath.join(self.path, "dir2")
        self.yadisk.mkdir(path1)
        self.yadisk.move(path1, path2)

        self.assertTrue(self.yadisk.exists(path2))

        self.yadisk.remove(path2, permanently=True)

    def test_remove_trash(self):
        path = posixpath.join(self.path, "dir-to-remove")
        origin_path = "disk:" + path

        self.yadisk.mkdir(path)
        self.yadisk.remove(path)

        trash_path = None

        for i in self.yadisk.trash_listdir("/"):
            if i.origin_path == origin_path:
                trash_path = i.path
                break

        self.assertTrue(trash_path is not None)

        self.yadisk.remove_trash(trash_path)
        self.assertFalse(self.yadisk.trash_exists(trash_path))

    def test_publish_unpublish(self):
        path = self.path

        self.yadisk.publish(path)
        self.assertIsNotNone(self.yadisk.get_meta(path).public_url)

        self.yadisk.unpublish(path)
        self.assertIsNone(self.yadisk.get_meta(path).public_url)

    def test_patch(self):
        path = self.path

        self.yadisk.patch(path, {"test_property": "I'm a value!"})
        self.assertEqual(self.yadisk.get_meta(path).custom_properties["test_property"], "I'm a value!")

        self.yadisk.patch(path, {"test_property": None})
        self.assertIsNone(self.yadisk.get_meta(path).custom_properties)

    def test_issue7(self):
        # See https://github.com/ivknv/yadisk/issues/7

        try:
            self.yadisk.public_listdir("any value here", path="any value here")
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
            self.yadisk.make_session(),
            "https://cloud-api.yandex.net/v1/disk/operations/123asd")
        self.assertTrue(is_operation_link(request.url))

        request = GetOperationStatusRequest(
            self.yadisk.make_session(),
            "http://cloud-api.yandex.net/v1/disk/operations/123asd")
        self.assertTrue(is_operation_link(request.url))
        self.assertTrue(request.url.startswith("https://"))

        request = GetOperationStatusRequest(
            self.yadisk.make_session(),
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
