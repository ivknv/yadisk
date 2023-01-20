#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup, find_packages

module_dir = os.path.dirname(__file__)

with codecs.open(os.path.join(module_dir, "README.rst"), encoding="utf8") as f:
    long_description = f.read()

setup(name="yadisk",
      version="1.2.18",
      packages=find_packages(exclude=("tests",)),
      description="Библиотека-клиент REST API Яндекс.Диска / Yandex.Disk REST API client library",
      long_description=long_description,
      author="Ivan Konovalov",
      author_email="ivknv0@gmail.com",
      license="LGPLv3",
      python_requires=">=3",
      install_requires=["requests"],
      url="https://github.com/ivknv/yadisk",
      project_urls={"Source code": "https://github.com/ivknv/yadisk",
                    "Documentation (EN)": "https://yadisk.readthedocs.io/en/latest",
                    "Documentation (RU)": "https://yadisk.readthedocs.io/ru/latest",
                    "Bug tracker": "https://github.com/ivknv/yadisk/issues"},
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
          "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
          "Topic :: Internet",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules"],
      keywords="yandex yandex.disk rest")
