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

from .utils import CaseInsensitiveDict

from ._typing_compat import Dict, Generator
from typing import Any, AnyStr, IO, Optional

__all__ = [
    "_apply_default_args", "_filter_request_kwargs",
    "_read_file_as_generator", "_set_authorization_header",
    "_add_authorization_header"
]


def _apply_default_args(args: Dict[str, Any], default_args: Dict[str, Any]) -> None:
    new_args = dict(default_args)
    new_args.update(args)
    args.clear()
    args.update(new_args)


def _filter_request_kwargs(kwargs: Dict[str, Any]) -> None:
    # Remove some of the yadisk-specific arguments from kwargs
    keys_to_remove = ("n_retries", "retry_interval", "fields", "overwrite", "path")

    for key in keys_to_remove:
        kwargs.pop(key, None)


def _read_file_as_generator(input_file: IO[AnyStr]) -> Generator[AnyStr, None, None]:
    chunk_size = 8192

    while chunk := input_file.read(chunk_size):
        yield chunk


def _set_authorization_header(
    kwargs: Dict[str, Any],
    new_token: Optional[str] = None
) -> None:
    headers = CaseInsensitiveDict(kwargs.get("headers", {}))

    if new_token:
        headers["Authorization"] = f"OAuth {new_token}"
    else:
        headers["Authorization"] = None

    kwargs["headers"] = headers

def _add_authorization_header(
    kwargs: Dict[str, Any],
    new_token: Optional[str] = None
) -> None:
    headers = CaseInsensitiveDict(kwargs.get("headers", {}))

    if "Authorization" in headers:
        return

    if new_token:
        headers["Authorization"] = f"OAuth {new_token}"
    else:
        headers["Authorization"] = None

    kwargs["headers"] = headers
