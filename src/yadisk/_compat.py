# -*- coding: utf-8 -*-
# Copyright © 2024 Ivan Konovalov

# This file is part of a Python library yadisk.

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, see <http://www.gnu.org/licenses/>.

__all__ = ["List", "Dict", "Set", "Tuple", "Callable", "Iterable", "Generator",
           "AsyncGenerator", "Coroutine", "Awaitable", "AsyncIterable",
           "Iterator", "AsyncIterator", "Mapping"]

import sys

from typing import Any

List: Any
Dict: Any
Set: Any
Tuple: Any

if sys.version_info.major == 3 and sys.version_info.minor < 9:
    from typing import (
        List, Dict, Set, Tuple, Callable, Iterable, Generator, AsyncGenerator,
        Coroutine, Awaitable, AsyncIterable, Iterator, AsyncIterator, Mapping
    )
else:
    from collections.abc import (
        Callable, Iterable, Generator, AsyncGenerator, Coroutine, Awaitable,
        AsyncIterable, Iterator, AsyncIterator, Mapping
    )

    List = list
    Dict = dict
    Set = set
    Tuple = tuple
