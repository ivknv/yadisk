# -*- coding: utf-8 -*-

__all__ = ["List", "Dict", "Set", "Tuple", "Callable", "Iterable", "Generator",
           "AsyncGenerator", "Coroutine", "Awaitable", "AsyncIterable",
           "Iterator", "AsyncIterator"]

import sys

from typing import Any

List: Any
Dict: Any
Set: Any
Tuple: Any

if sys.version_info.major == 3 and sys.version_info.minor < 9:
    from typing import (
        List, Dict, Set, Tuple, Callable, Iterable, Generator, AsyncGenerator,
        Coroutine, Awaitable, AsyncIterable, Iterator, AsyncIterator
    )
else:
    from collections.abc import (
        Callable, Iterable, Generator, AsyncGenerator, Coroutine, Awaitable,
        AsyncIterable, Iterator, AsyncIterator
    )

    List = list
    Dict = dict
    Set = set
    Tuple = tuple
