#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

__all__ = ["ID", "SECRET", "TOKEN", "load", "store"]

ID = ""
SECRET = ""
TOKEN = ""
PATH = ""

def load():
    global ID, SECRET, TOKEN, PATH

    with open("app_info.json") as f:
        info = json.loads(f.read())

    ID, SECRET, TOKEN = info["id"], info["secret"], info["token"]
    PATH = info["path"]

def store():
    with open("app_info.json", "w") as f:
        f.write(json.dumps({"id":     ID,
                            "secret": SECRET,
                            "token":  TOKEN,
                            "path":   PATH}))
