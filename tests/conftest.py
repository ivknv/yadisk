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


@pytest.fixture
def disk_root(request: pytest.FixtureRequest) -> str:
    path = os.environ["PYTHON_YADISK_TEST_ROOT"]

    # Get rid of 'disk:/' prefix in the path and make it start with a slash
    # for consistency
    if path.startswith("disk:/"):
        path = posixpath.join("/", path[len("disk:/"):])

    if len([i for i in path.split("/") if i]) < 1:
        raise ValueError("PYTHON_YADISK_TEST_ROOT set to /")

    test_name = request.function.__name__

    return posixpath.join(path, test_name)


@pytest.fixture()
def disk_cleanup(
    disk_root: str,
    client: yadisk.Client,
    poll_interval: float
) -> Generator[None, None, None]:
    try:
        client.mkdir(disk_root)
    except yadisk.exceptions.DirectoryExistsError:
        pass
    except yadisk.exceptions.ParentNotFoundError:
        client.mkdir(posixpath.split(disk_root)[0])
        client.mkdir(disk_root)

    yield

    try:
        client.remove(
            disk_root,
            permanently=True,
            poll_interval=poll_interval
        )
    except yadisk.utils._UnexpectedRequestError:
        pass


@pytest.fixture()
async def async_disk_cleanup(
    disk_root: str,
    async_client: yadisk.AsyncClient,
    poll_interval: float
) -> AsyncGenerator[None, None]:
    try:
        await async_client.mkdir(disk_root)
    except yadisk.exceptions.DirectoryExistsError:
        pass
    except yadisk.exceptions.ParentNotFoundError:
        await async_client.mkdir(posixpath.split(disk_root)[0])
        await async_client.mkdir(disk_root)

    yield

    try:
        await async_client.remove(
            disk_root,
            permanently=True,
            poll_interval=poll_interval
        )
    except yadisk.utils._UnexpectedRequestError:
        pass


@pytest.fixture(scope="package")
def replay_enabled() -> bool:
    return os.environ.get("PYTHON_YADISK_REPLAY_ENABLED", "1") == "1"


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

    if recording_enabled and replay_enabled:
        raise ValueError("Both recording and replay enabled at the same time")

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


@pytest.fixture
def sync_client_test(record_or_replay, disk_cleanup) -> None:
    pass


@pytest.fixture
def async_client_test(record_or_replay, async_disk_cleanup) -> None:
    pass


@pytest.fixture
def poll_interval(replay_enabled: bool) -> float:
    return 0.0 if replay_enabled else 1.0
