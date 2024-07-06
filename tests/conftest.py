# -*- coding: utf-8 -*-

import inspect
import posixpath
import os

from .test_session import TestSession, AsyncTestSession
from .disk_gateway import BackgroundGatewayThread

import yadisk
from yadisk._typing_compat import Generator, AsyncGenerator

import pytest


@pytest.fixture(scope="package")
def gateway_host() -> str:
    return os.environ.get("PYTHON_YADISK_GATEWAY_HOST", "0.0.0.0")


@pytest.fixture(scope="package")
def gateway_port() -> int:
    return int(os.environ.get("PYTHON_YADISK_GATEWAY_PORT", "8080"))


@pytest.fixture(scope="package")
def gateway(gateway_host: str, gateway_port: int) -> Generator[BackgroundGatewayThread, None, None]:
    gateway = BackgroundGatewayThread(gateway_host, gateway_port)
    gateway.start()

    # Make sure the actual API token won't be exposed in the recorded requests
    gateway.client.update_token_map({
        os.environ["PYTHON_YADISK_APP_TOKEN"]: "supposedly_valid_token"
    })

    yield gateway

    gateway.stop()


@pytest.fixture(scope="package")
def disk_root() -> str:
    path = os.environ["PYTHON_YADISK_TEST_ROOT"]

    # Get rid of 'disk:/' prefix in the path and make it start with a slash
    # for consistency
    if path.startswith("disk:/"):
        path = posixpath.join("/", path[len("disk:/"):])

    return path


@pytest.fixture(scope="package")
def replay_enabled() -> bool:
    return os.environ.get("PYTHON_YADISK_REPLAY_ENABLED", "0") == "1"


@pytest.fixture(scope="package")
def recording_enabled() -> bool:
    return os.environ.get("PYTHON_YADISK_RECORDING_ENABLED", "0") == "1"


@pytest.fixture
def record_or_replay(
    request: pytest.FixtureRequest,
    gateway: BackgroundGatewayThread,
    recording_enabled: bool,
    replay_enabled: bool
) -> Generator[None, None, None]:
    if inspect.iscoroutinefunction(request.function):
        directory = os.path.join("tests", "recorded", "async")
    else:
        directory = os.path.join("tests", "recorded", "sync")

    test_name = request.function.__name__

    if recording_enabled:
        os.makedirs(directory, exist_ok=True)

        with gateway.client.record_as(os.path.join(directory, f"{test_name}.json")):
            yield
    elif replay_enabled:
        with gateway.client.replay(os.path.join(directory, f"{test_name}.json")):
            yield
    else:
        yield


@pytest.fixture(scope="class", params=["requests", "httpx", "pycurl"])
def client(
    request: pytest.FixtureRequest,
    gateway_host: str,
    gateway_port: int,
    replay_enabled: bool,
    recording_enabled: bool
) -> Generator[yadisk.Client, None, None]:
    base_gateway_url = f"http://{gateway_host}:{gateway_port}"

    if replay_enabled:
        test_session = TestSession(
            yadisk.import_session(request.param)(),
            disk_base_url=f"{base_gateway_url}/replay/response/disk",
            auth_base_url=f"{base_gateway_url}/replay/response/auth",
            download_base_url=f"{base_gateway_url}/replay/response/download",
            upload_base_url=f"{base_gateway_url}/replay/response/upload"
        )
    else:
        test_session = TestSession(
            yadisk.import_session(request.param)(),
            disk_base_url=f"{base_gateway_url}/forward/disk",
            auth_base_url=f"{base_gateway_url}/forward/auth",
            download_base_url=f"{base_gateway_url}/forward/download",
            upload_base_url=f"{base_gateway_url}/forward/upload"
        )

    with yadisk.Client(
        os.environ["PYTHON_YADISK_APP_ID"],
        os.environ["PYTHON_YADISK_APP_SECRET"],
        os.environ["PYTHON_YADISK_APP_TOKEN"],
        session=test_session
    ) as client:
        client.default_args.update({"n_retries": 50})
        yield client


@pytest.fixture(scope="class", params=["aiohttp", "httpx"])
async def async_client(
    request: pytest.FixtureRequest,
    gateway_host: str,
    gateway_port: int,
    replay_enabled: bool,
    recording_enabled: bool
) -> AsyncGenerator[yadisk.AsyncClient, None]:
    base_gateway_url = f"http://{gateway_host}:{gateway_port}"

    if replay_enabled:
        test_session = AsyncTestSession(
            yadisk.import_async_session(request.param)(),
            disk_base_url=f"{base_gateway_url}/replay/response/disk",
            auth_base_url=f"{base_gateway_url}/replay/response/auth",
            download_base_url=f"{base_gateway_url}/replay/response/download",
            upload_base_url=f"{base_gateway_url}/replay/response/upload"
        )
    else:
        test_session = AsyncTestSession(
            yadisk.import_async_session(request.param)(),
            disk_base_url=f"{base_gateway_url}/forward/disk",
            auth_base_url=f"{base_gateway_url}/forward/auth",
            download_base_url=f"{base_gateway_url}/forward/download",
            upload_base_url=f"{base_gateway_url}/forward/upload"
        )

    async with yadisk.AsyncClient(
        os.environ["PYTHON_YADISK_APP_ID"],
        os.environ["PYTHON_YADISK_APP_SECRET"],
        os.environ["PYTHON_YADISK_APP_TOKEN"],
        session=test_session
    ) as async_client:
        async_client.default_args.update({"n_retries": 50})
        yield async_client


@pytest.fixture(scope="package")
def anyio_backend() -> str:
    return "asyncio"
