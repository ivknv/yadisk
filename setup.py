#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name="yadisk",
      version="0.1.0",
      packages=find_packages(),
      description="Yandex.Disk REST API client library",
      author="Ivan Konovalov",
      author_email="rvan.mega@gmail.com",
      license="GPLv3",
      python_requires=">=3",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
          "Topic :: Internet",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules"],
      keywords="yandex yandex.disk rest")
