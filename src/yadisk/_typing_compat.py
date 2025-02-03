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

__all__ = [
    "AsyncGenerator",
    "AsyncIterable",
    "AsyncIterator",
    "Awaitable",
    "Callable",
    "Coroutine",
    "Dict",
    "Generator",
    "Iterable",
    "Iterator",
    "List",
    "Mapping",
    "Set",
    "Tuple",
    "Type",
    "TypeAlias"
]

import sys

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from typing import TYPE_CHECKING

if sys.version_info < (3, 10):
    from typing import (
        List, Dict, Set, Tuple, Callable, Iterable, Generator, AsyncGenerator,
        Coroutine, Awaitable, AsyncIterable, Iterator, AsyncIterator, Mapping,
        Type
    )
else:
    from collections.abc import (
        Callable, Iterable, Generator, AsyncGenerator, Coroutine, Awaitable,
        AsyncIterable, Iterator, AsyncIterator, Mapping
    )

    if TYPE_CHECKING:  # pragma: no cover
        from typing import List, Dict, Set, Tuple, Type
    else:
        # mypy complains about this
        List = list
        Dict = dict
        Set = set
        Tuple = tuple
        Type = type
