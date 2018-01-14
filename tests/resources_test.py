#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import random

import posixpath
from unittest import TestCase
from io import BytesIO

from . import config

import yadisk.objects

original_send = requests.Session.send

def patched_send(self, *args, **kwargs):
    response = original_send(self, *args, **kwargs)

    # Fake a random server error
    #if random.randint(1, 250) == 1:
    #    response.status_code = 500

    return response

requests.Session.send = patched_send

class ResourcesTestCase(TestCase):
    def setUp(self):
        self.yadisk = yadisk.YaDisk(config.ID, config.SECRET, config.TOKEN)
        self.path = config.PATH

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
        buf1, buf2 = BytesIO(), BytesIO()

        buf1.write(b"0" * 1024**2)
        buf1.seek(0)

        path = posixpath.join(self.path, "zeroes.txt")

        self.yadisk.upload(buf1, path, overwrite=True, n_retries=3)
        self.yadisk.download(path, buf2, n_retries=3)
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

    def test_move(self):
        path1 = posixpath.join(self.path, "dir1")
        path2 = posixpath.join(self.path, "dir2")
        self.yadisk.mkdir(path1)
        self.yadisk.move(path1, path2)

        self.assertTrue(self.yadisk.exists(path2))

        self.yadisk.remove(path2, permanently=True)

    def test_remove_trash(self):
        path = posixpath.join(self.path, "dir-to-remove")
        self.yadisk.mkdir(path)
        self.yadisk.remove(path)
        self.yadisk.remove_trash("dir-to-remove")
        self.assertFalse(self.yadisk.trash_exists("dir-to-remove"))

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
