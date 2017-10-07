#!/usr/bin/env python
# -*- coding: utf-8 -*-

import posixpath
from unittest import TestCase
from io import BytesIO

from . import config

import yadisk.objects

class ResourcesTestCase(TestCase):
    def setUp(self):
        self.yadisk = yadisk.YaDisk(config.ID, config.SECRET, config.TOKEN)
        self.path = config.PATH

    def test_get_meta(self):
       self.assertIsInstance(self.yadisk.get_meta(self.path), yadisk.objects.ResourceObject)

    def test_mkdir_and_exists(self):
        names = ["dir1", "dir2", "dir3"]

        for name in names:
            path = posixpath.join(self.path, name)

            self.yadisk.mkdir(path)
            self.assertTrue(self.yadisk.exists(path))

            self.yadisk.remove(path, permanently=True)
            self.assertFalse(self.yadisk.exists(path))

    def test_upload_and_download(self):
        buf1, buf2 = BytesIO(), BytesIO()

        buf1.write(b"0" * 1024**2)
        buf1.seek(0)

        path = posixpath.join(self.path, "zeroes.txt")

        self.yadisk.upload(buf1, path, overwrite=True)
        self.assertTrue(self.yadisk.download(path, buf2))
        self.yadisk.remove(path, permanently=True)

        buf1.seek(0)
        buf2.seek(0)

        self.assertEqual(buf1.read(), buf2.read())

    def test_check_token(self):
        self.assertTrue(self.yadisk.check_token())
        self.assertFalse(self.yadisk.check_token("asdasdasd"))

    def test_permanent_remove(self):
        path = posixpath.join(self.path, "dir")

        self.yadisk.mkdir(path)
        self.yadisk.remove(path, permanently=True)
        self.assertFalse(self.yadisk.trash_exists(path))

    def test_restore_trash(self):
        path = posixpath.join(self.path, "dir")

        self.yadisk.mkdir(path)
        self.yadisk.remove(path)
        self.yadisk.restore_trash("dir", path)
        self.assertTrue(self.yadisk.exists(path))
        self.yadisk.remove(path, permanently=True)
