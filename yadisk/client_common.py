# -*- coding: utf-8 -*-

from .common import CaseInsensitiveDict

from .compat import Dict, Generator
from typing import Any, AnyStr, IO, Optional

__all__ = [
    "_apply_default_args", "_filter_request_kwargs",
    "_read_file_as_generator", "_replace_authorization_header"
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


def _replace_authorization_header(
    kwargs: Dict[str, Any],
    new_token: Optional[str] = None
) -> None:
    headers = CaseInsensitiveDict(kwargs.get("headers", {}))

    if new_token:
        headers["Authorization"] = f"OAuth {new_token}"
    else:
        headers["Authorization"] = None

    kwargs["headers"] = headers
