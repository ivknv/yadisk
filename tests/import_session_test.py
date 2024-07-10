# -*- coding: utf-8 -*-

import pytest
import yadisk
from yadisk._typing_compat import List

import typing


@pytest.fixture
def available_session_names() -> List[str]:
    return [typing.get_args(literal)[0] for literal in typing.get_args(yadisk.types.SessionName)]


@pytest.fixture
def available_async_session_names() -> List[str]:
    return [typing.get_args(literal)[0] for literal in typing.get_args(yadisk.types.AsyncSessionName)]


@pytest.mark.parametrize(
    "name, expected_class_name",
    [("requests", "RequestsSession"), ("httpx", "HTTPXSession"), ("pycurl", ("PycURLSession"))]
)
def test_import_session(
    name: yadisk.types.SessionName,
    expected_class_name: str,
    available_session_names: List[str]
) -> None:
    assert name in available_session_names
    assert yadisk.import_session(name).__name__ == expected_class_name


@pytest.mark.parametrize(
    "name, expected_class_name",
    [("aiohttp", "AIOHTTPSession"), ("httpx", "AsyncHTTPXSession")]
)
def test_import_async_session(
    name: yadisk.types.AsyncSessionName,
    expected_class_name: str,
    available_async_session_names: List[str]
) -> None:
    assert name in available_async_session_names
    assert yadisk.import_async_session(name).__name__ == expected_class_name


def test_import_unknown_session() -> None:
    with pytest.raises(ValueError):
        yadisk.import_session(typing.cast(typing.Any, "notreal"))

    with pytest.raises(ValueError):
        yadisk.import_async_session(typing.cast(typing.Any, "notreal"))
