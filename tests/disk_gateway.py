# -*- coding: utf-8 -*-

import argparse
import threading
import time
from typing import Any
from urllib.parse import urlencode, quote, quote_plus
import base64
import asyncio
import zlib
import contextlib
import json

import httpx

from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from starlette.routing import Route

import uvicorn

__all__ = [
    "BackgroundGatewayThread",
    "DiskGateway",
    "DiskGatewayClient",
    "main"
]

YADISK_BASE_URL = "https://cloud-api.yandex.net"
AUTH_BASE_URL = "https://oauth.yandex.ru"
DOWNLOAD_BASE_URL = "https://downloader.disk.yandex.ru"

RELEVANT_REQUEST_HEADERS = ["content-type", "connection", "authorization"]
RELEVANT_RESPONSE_HEADERS = ["content-type", "content-length"]


def get_upload_base_url(subdomain: str) -> str:
    return f"https://{subdomain}.disk.yandex.net:443"


def select_keys(d, keys):
    return {key: d[key] for key in keys if key in d}


def serialize_content(content: bytes) -> str:
    return base64.b64encode(zlib.compress(content)).decode("utf8")


def deserialize_content(content: str) -> bytes:
    return zlib.decompress(base64.b64decode(content))


def serialize_request(request: httpx.Request, response: httpx.Response):
    return {
        "method":   request.method,
        "url":      str(request.url),
        "headers":  select_keys(request.headers, RELEVANT_REQUEST_HEADERS),
        "content":  serialize_content(request.content),
        "response": serialize_response(response)
    }


def deserialize_request(request: dict):
    return (
        httpx.Request(
            request["method"],
            request["url"],
            headers=request["headers"],
            content=deserialize_content(request["content"])
        ),
        deserialize_response(request["response"])
    )


def deserialize_response(response: dict) -> httpx.Response:
    return httpx.Response(
        status_code=response["status_code"],
        headers=response["headers"],
        content=deserialize_content(response["content"])
    )


def serialize_response(response: httpx.Response):
    return {
        "status_code": response.status_code,
        "headers":     select_keys(response.headers, RELEVANT_RESPONSE_HEADERS),
        "content":     serialize_content(response.content)
    }


class UnexpectedRequestResponse(JSONResponse):
    def __init__(self, message: str) -> None:
        super().__init__(
            {
                "error":       "_UnexpectedRequestError",
                "description": "unexpected request",
                "message":     message
            },
            status_code=499
        )


class DiskGateway:
    def __init__(self):
        self.routes = [
            Route(
                "/forward/disk",
                endpoint=self.disk_gateway,
                methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
            ),
            Route(
                "/forward/disk/{path:path}",
                endpoint=self.disk_gateway,
                methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
            ),

            Route("/forward/auth",             endpoint=self.auth_gateway, methods=["POST"]),
            Route("/forward/auth/{path:path}", endpoint=self.auth_gateway, methods=["POST"]),

            Route("/forward/download",             endpoint=self.download_gateway, methods=["GET"]),
            Route("/forward/download/{path:path}", endpoint=self.download_gateway, methods=["GET"]),

            Route(
                "/forward/upload/{subdomain}",
                endpoint=self.upload_gateway,
                methods=["PUT"]
            ),
            Route(
                "/forward/upload/{subdomain}/{path:path}",
                endpoint=self.upload_gateway,
                methods=["PUT"]
            ),

            Route("/record/start", endpoint=self.start_recording,         methods=["POST"]),
            Route("/record/stop",  endpoint=self.stop_recording,          methods=["POST"]),
            Route("/record/clear", endpoint=self.clear_recorded_requests, methods=["POST"]),
            Route("/record/json",  endpoint=self.dump_recorded_requests,  methods=["GET"]),

            Route("/replay/set/{index:int}", endpoint=self.set_replay_index, methods=["POST"]),
            Route("/replay/set",             endpoint=self.set_replay,       methods=["POST"]),

            Route(
                "/replay/response/disk",
                endpoint=self.disk_replay,
                methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
            ),
            Route(
                "/replay/response/disk/{path:path}",
                endpoint=self.disk_replay,
                methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
            ),

            Route("/replay/response/auth",             endpoint=self.auth_replay, methods=["POST"]),
            Route("/replay/response/auth/{path:path}", endpoint=self.auth_replay, methods=["POST"]),

            Route("/replay/response/download",             endpoint=self.download_replay, methods=["GET"]),
            Route("/replay/response/download/{path:path}", endpoint=self.download_replay, methods=["GET"]),

            Route(
                "/replay/response/upload/{subdomain}",
                endpoint=self.upload_replay,
                methods=["PUT"]
            ),
            Route(
                "/replay/response/upload/{subdomain}/{path:path}",
                endpoint=self.upload_replay,
                methods=["PUT"]
            ),

            Route("/status", endpoint=self.check_status, methods=["GET"]),

            Route("/tokens/update", endpoint=self.update_token_map, methods=["POST"]),
            Route("/tokens/clear", endpoint=self.clear_token_map, methods=["POST"])
        ]

        @contextlib.asynccontextmanager
        async def lifespan(_: Starlette):
            async with self.client:
                yield

        self.app = Starlette(debug=True, routes=self.routes, lifespan=lifespan)

        self.client = httpx.AsyncClient()
        self.recorded_requests = []
        self.recording_enabled = False
        self.current_request_index = 0
        self.server_task = None

        # This is used to substitute real OAuth token values for fake ones to
        # not expose them
        # Keys are actual OAuth tokens that will be sent to the Yandex.Disk API,
        # values are made up values that will be put in the recorded requests
        self.tokens = {}

    async def on_shutdown(self):
        await self.client.aclose()

    async def update_token_map(self, request: Request):
        js = await request.json()

        # We expect a JSON object like {"real token": "token substitute"}
        if not isinstance(js, dict):
            return Response(status_code=422)

        # This doesn't look thread-safe, but it's not important for testing anyway
        self.tokens.update(js)

        return Response(status_code=204)

    async def clear_token_map(self, request: Request):
        self.tokens.clear()
        return Response(status_code=204)

    async def forward_request(self, request: Request, base_url: str):
        path: str = request.path_params.get("path", "")
        content: bytes = await request.body()

        authorization_header = request.headers.get("authorization", "")

        _, _, real_token = authorization_header.rpartition(" ")
        test_token = self.tokens.get(real_token, real_token)

        outgoing_request = httpx.Request(
            request.method,
            f"{base_url}/{path}",
            params=request.query_params,
            content=content,
            headers=select_keys(request.headers, RELEVANT_REQUEST_HEADERS)
        )

        server_response = await self.client.send(outgoing_request, follow_redirects=True)

        response = Response(
            content=server_response.content,
            status_code=server_response.status_code
        )

        if "content-type" in server_response.headers:
            response.headers["Content-Type"] = server_response.headers["content-type"]

        if self.recording_enabled:
            # Substitute the Authorization header to hide the OAuth token
            if test_token:
                outgoing_request.headers["authorization"] = f"OAuth {test_token}"
            else:
                outgoing_request.headers.pop("authorization", None)

            self.recorded_requests.append(serialize_request(outgoing_request, server_response))

        return response

    async def replay_response(self, request: Request, base_url: str):
        try:
            serialized_request = self.recorded_requests[self.current_request_index]
        except IndexError:
            return UnexpectedRequestResponse("did not expect any more requests")

        path = request.path_params.get("path", "")

        content: bytes = await request.body()
        headers = select_keys(request.headers, RELEVANT_REQUEST_HEADERS)

        # Substitute the real token for the test one
        # Recorded requests contain a test OAuth token instead of the real one
        authorization_header = request.headers.get("authorization", "")
        _, _, real_token = authorization_header.rpartition(" ")
        test_token = self.tokens.get(real_token, real_token)

        if test_token:
            headers["authorization"] = f"OAuth {test_token}"

        expected_request, expected_response = deserialize_request(serialized_request)

        url_without_params = f"{base_url}/{path}"

        if request.query_params:
            url = url_without_params + "?" + urlencode(request.query_params, quote_via=quote)
        else:
            url = url_without_params

        if url != expected_request.url:
            # Try alternate urlencode method
            url =  url_without_params + "?" + urlencode(request.query_params, quote_via=quote_plus)

            return UnexpectedRequestResponse(
                f"requests's URL doesn't match. Expected URL: {expected_request.url}, got: {url}"
            )

        expected_headers = select_keys(expected_request.headers, RELEVANT_REQUEST_HEADERS)

        for key, value in expected_headers.items():
            key = key.lower()

            if key not in headers:
                return UnexpectedRequestResponse(f"request is missing header {key}: {value}")

            if headers[key] != value:
                return UnexpectedRequestResponse(
                    f"requests's header doesn't match. Expected header: {key}: {value}, got: {key}: {headers[key]}"
                )

        for key, value in headers.items():
            key = key.lower()

            if key not in expected_headers:
                return UnexpectedRequestResponse(f"got unexpected header {key}: {value}")

            if expected_headers[key] != value:
                return UnexpectedRequestResponse(
                    f"requests's header doesn't match. Expected header: {key}: {headers[key]}, got: {key}: {value}"
                )

        if url != expected_request.url:
            return UnexpectedRequestResponse(
                f"requests's URL doesn't match. Expected URL: {expected_request.url}, got: {url}"
            )

        if request.method != expected_request.method:
            return UnexpectedRequestResponse(
                f"requests's method doesn't match. Expected method: {expected_request.method}, got: {request.method}"
            )

        if content != expected_request.content:
            return UnexpectedRequestResponse("requests's content doesn't match.")

        self.current_request_index += 1

        return Response(
            content=expected_response.content,
            status_code=expected_response.status_code,
            headers=expected_response.headers
        )

    async def disk_gateway(self, request: Request):
        return await self.forward_request(request, YADISK_BASE_URL)

    async def auth_gateway(self, request: Request):
        return await self.forward_request(request, AUTH_BASE_URL)

    async def download_gateway(self, request: Request):
        return await self.forward_request(request, DOWNLOAD_BASE_URL)

    async def upload_gateway(self, request: Request):
        subdomain = request.path_params["subdomain"]

        return await self.forward_request(request, get_upload_base_url(subdomain))

    async def disk_replay(self, request: Request):
        return await self.replay_response(request, YADISK_BASE_URL)

    async def auth_replay(self, request: Request):
        return await self.replay_response(request, AUTH_BASE_URL)

    async def download_replay(self, request: Request):
        return await self.replay_response(request, DOWNLOAD_BASE_URL)

    async def upload_replay(self, request: Request):
        subdomain = request.path_params["subdomain"]

        return await self.replay_response(request, get_upload_base_url(subdomain))

    async def start_recording(self, request: Request):
        self.recording_enabled = True

        return Response(status_code=204)

    async def stop_recording(self, request: Request):
        self.recording_enabled = False

        return Response(status_code=204)

    async def clear_recorded_requests(self, request: Request):
        self.recorded_requests.clear()
        self.current_request_index = 0

        return Response(status_code=204)

    async def dump_recorded_requests(self, request: Request):
        return JSONResponse(self.recorded_requests)

    async def set_replay_index(self, request: Request):
        self.current_request_index = int(request.path_params.get("index", "0"))

        return Response(status_code=204)

    async def set_replay(self, request: Request):
        self.recorded_requests = await request.json()
        self.current_request_index = 0

        return Response(status_code=204)

    async def check_status(self, request: Request):
        return Response(status_code=204)

    def stop(self):
        if self.server_task is not None:
            self.server_task.cancel()

    async def run(self, host: str, port: int):
        config = uvicorn.Config(self.app, host=host, port=port, log_level="error")
        server = uvicorn.Server(config)

        self.server_task = asyncio.create_task(server.serve())

        try:
            await self.server_task
        except asyncio.CancelledError:
            await server.shutdown()


async def main(args: list) -> None:
    parser = argparse.ArgumentParser(description="Yandex.Disk test gateway")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8080, help="Server port")

    ns = parser.parse_args(args)

    await DiskGateway().run(ns.host, ns.port)


class DiskGatewayClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._client = httpx.Client()

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self._client.__exit__(*args, **kwargs)

    def close(self):
        self._client.close()

    def start_recording(self):
        self._client.post(f"{self.base_url}/record/start").raise_for_status()

    def stop_recording(self):
        self._client.post(f"{self.base_url}/record/stop").raise_for_status()

    def clear_recorded_requests(self):
        self._client.post(f"{self.base_url}/record/clear").raise_for_status()

    def dump_recorded_requests(self):
        return self._client.get(f"{self.base_url}/record/json").json()

    def set_replay_index(self, index: int):
        self._client.get(f"{self.base_url}/replay/set/{index}").raise_for_status()

    def set_replay(self, json: Any):
        self._client.post(f"{self.base_url}/replay/set", json=json).raise_for_status()

    def is_running(self) -> bool:
        try:
            return self._client.get(f"{self.base_url}/status").status_code == 204
        except httpx.ConnectError:
            return False

    def update_token_map(self, tokens: dict):
        return self._client.post(f"{self.base_url}/tokens/update", json=tokens).raise_for_status()

    def clear_token_map(self):
        return self._client.post(f"{self.base_url}/tokens/clear").raise_for_status()

    @contextlib.contextmanager
    def record_as(self, filename: str):
        self.start_recording()
        yield

        self.stop_recording()
        recorded_requests = self.dump_recorded_requests()

        with open(filename, "w") as output:
            json.dump(recorded_requests, output, indent=4)

        self.clear_recorded_requests()

    @contextlib.contextmanager
    def replay(self, filename: str):
        with open(filename, "r") as in_file:
            recorded_requests = json.load(in_file)
            self.set_replay(recorded_requests)

        yield

        self.clear_recorded_requests()


class BackgroundGatewayThread:
    def __init__(self, host: str, port: int):
        self.disk_gateway = DiskGateway()

        self.client = DiskGatewayClient(f"http://{host}:{port}")

        self.server_thread = threading.Thread(
            target=asyncio.run,
            args=(self.disk_gateway.run(host, port),)
        )

    def start(self):
        self.server_thread.start()

        while not self.client.is_running():
            time.sleep(0.01)

    def stop(self):
        self.disk_gateway.stop()
        self.client.close()
        self.server_thread.join()


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main(sys.argv[1:]))
