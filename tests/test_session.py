# -*- coding: utf-8 -*-

import yadisk
from yadisk.types import HTTPMethod

from urllib.parse import urljoin, urlparse

from typing import Optional

__all__ = ["AsyncTestSession", "TestSession"]

def _ensure_trailing_slash(s: str) -> str:
    if not s.endswith("/"):
        return s + "/"

    return s

class TestSession(yadisk.Session):
    __test__ = False

    def __init__(
        self,
        session:           yadisk.Session,
        disk_base_url:     Optional[str] = None,
        auth_base_url:     Optional[str] = None,
        download_base_url: Optional[str] = None,
        upload_base_url:   Optional[str] = None
    ):
        self._session          = session
        self.disk_base_url     = disk_base_url
        self.auth_base_url     = auth_base_url
        self.download_base_url = download_base_url
        self.upload_base_url   = upload_base_url

    def send_request(self, method: HTTPMethod, url: str, **kwargs) -> yadisk.Response:
        url_parsed = urlparse(url)
        kwargs.setdefault("headers", {})

        new_base_url: Optional[str] = None

        if url_parsed.hostname == "cloud-api.yandex.net":
            new_base_url = self.disk_base_url
        elif url_parsed.hostname == "oauth.yandex.ru":
            new_base_url = self.auth_base_url
        elif url_parsed.hostname == "downloader.disk.yandex.ru":
            new_base_url = self.download_base_url
        else:
            subdomain, _, domain = (url_parsed.hostname or "").partition(".")

            assert domain == "disk.yandex.net", f"Got unexpected URL: {url}"
            assert subdomain.startswith("uploader"), f"Got unexpected URL: {url}"

            if self.upload_base_url is not None:
                new_base_url = f"{self.upload_base_url.rstrip('/')}/{subdomain}"

        if new_base_url is not None:
            url = urljoin(_ensure_trailing_slash(new_base_url), url_parsed.path.lstrip("/"))
            if url_parsed.query:
                url += "?" + url_parsed.query

        return self._session.send_request(method, url, **kwargs)

    def close(self) -> None:
        self._session.close()

class AsyncTestSession(yadisk.AsyncSession):
    __test__ = False

    def __init__(
        self,
        session:           yadisk.AsyncSession,
        disk_base_url:     Optional[str] = None,
        auth_base_url:     Optional[str] = None,
        download_base_url: Optional[str] = None,
        upload_base_url:   Optional[str] = None,
    ):
        self._session          = session
        self.disk_base_url     = disk_base_url
        self.auth_base_url     = auth_base_url
        self.download_base_url = download_base_url
        self.upload_base_url   = upload_base_url

    async def send_request(self, method: HTTPMethod, url: str, **kwargs) -> yadisk.AsyncResponse:
        url_parsed = urlparse(url)
        kwargs.setdefault("headers", {})

        new_base_url: Optional[str] = None

        if url_parsed.hostname == "cloud-api.yandex.net":
            new_base_url = self.disk_base_url
        elif url_parsed.hostname == "oauth.yandex.ru":
            new_base_url = self.auth_base_url
        elif url_parsed.hostname == "downloader.disk.yandex.ru":
            new_base_url = self.download_base_url
        else:
            subdomain, _, domain = (url_parsed.hostname or "").partition(".")

            assert domain == "disk.yandex.net", f"Got unexpected URL: {url}"
            assert subdomain.startswith("uploader"), f"Got unexpected URL: {url}"

            if self.upload_base_url is not None:
                new_base_url = f"{self.upload_base_url.rstrip('/')}/{subdomain}"

        if new_base_url is not None:
            url = urljoin(_ensure_trailing_slash(new_base_url), url_parsed.path.lstrip("/"))
            if url_parsed.query:
                url += "?" + url_parsed.query

        return await self._session.send_request(method, url, **kwargs)

    async def close(self) -> None:
        await self._session.close()
