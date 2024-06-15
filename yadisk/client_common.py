# -*- coding: utf-8 -*-

from .common import CaseInsensitiveDict

from .compat import Dict, Generator
from typing import Any, AnyStr, IO, Optional

__all__ = [
    "_apply_default_args", "_filter_request_kwargs",
    "_read_file_as_generator", "_replace_authorization_header",
    "_map_base_url_for_auth", "_map_base_url_for_disk", "_replace_url_domain",
    "_replace_upload_url_domain"
]

def _apply_default_args(args: Dict[str, Any], default_args: Dict[str, Any]) -> None:
    new_args = dict(default_args)
    new_args.update(args)
    args.clear()
    args.update(new_args)

def _filter_request_kwargs(kwargs: Dict[str, Any]) -> None:
    # Remove some of the yadisk-specific arguments from kwargs
    keys_to_remove = (
        "n_retries", "retry_interval", "fields", "overwrite", "path", "base_url",
        "auth_base_url", "disk_base_url", "download_base_url", "upload_base_url"
    )

    for key in keys_to_remove:
        kwargs.pop(key, None)

def _read_file_as_generator(input_file: IO[AnyStr]) -> Generator[AnyStr, None, None]:
    chunk_size = 8192

    while chunk := input_file.read(chunk_size):
        yield chunk

def _replace_authorization_header(kwargs: Dict[str, Any], new_token: Optional[str] = None) -> None:
    headers = CaseInsensitiveDict(kwargs.get("headers", {}))

    if new_token:
        headers["Authorization"] = f"OAuth {new_token}"
    else:
        headers["Authorization"] = None

    kwargs["headers"] = headers

def _map_base_url_for_auth(kwargs: Dict[str, Any]) -> None:
    if "auth_base_url" in kwargs:
        kwargs["base_url"] = kwargs.pop("auth_base_url")

    kwargs.pop("disk_base_url", None)
    kwargs.pop("download_base_url", None)
    kwargs.pop("upload_base_url", None)

def _map_base_url_for_disk(kwargs: Dict[str, Any]) -> None:
    if "disk_base_url" in kwargs:
        kwargs["base_url"] = kwargs.pop("disk_base_url")

    kwargs.pop("auth_base_url", None)
    kwargs.pop("download_base_url", None)
    kwargs.pop("upload_base_url", None)

def _replace_url_domain(url: str, new_base_url: str) -> str:
    schema, _, rest = url.partition("://")
    netloc, _, rest = rest.partition("/")

    return f"{new_base_url}/{rest}"

def _replace_upload_url_domain(url: str, new_base_url: str) -> str:
    # This one has to work a little different, because upload URLs have a
    # random subdomain, we have to pass along it somehow
    schema, _, rest = url.partition("://")
    netloc, _, rest = rest.partition("/")
    subdomain, _, _ = netloc.partition(".")

    return f"{new_base_url}/{subdomain}/{rest}"
