# -*- coding: utf-8 -*-

__all__ = ["List", "Dict", "Set", "Tuple", "Callable", "Iterable", "Generator",
           "AsyncGenerator", "Coroutine", "Awaitable", "AsyncIterable",
           "Iterator", "AsyncIterator", "Self"]

import sys

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

if sys.version_info.major == 3 and sys.version_info.minor < 11:
    from typing_extensions import Self
else:
    from typing import Self
