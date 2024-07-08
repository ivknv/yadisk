# -*- coding: utf-8 -*-

import os

import pytest
import yadisk

confirmation_code = "5320215"

replay_enabled = os.environ.get("PYTHON_YADISK_REPLAY_ENABLED", "1") != "1"
device_id = "test device 123"

# Recording data for these tests requires human intervention
# NOTE: If you re-record these tests, make sure you change the
# application secret afterwards and ensure that none of the captured
# tokens are valid, otherwise you may end up leaking that data

@pytest.mark.skipif(
    replay_enabled,
    reason="this test has to be explicitly modified to be run outside of replay mode"
)
@pytest.mark.usefixtures("record_or_replay")
def test_auth(client: yadisk.Client) -> None:
    token = client.get_token(confirmation_code, device_id=device_id)

    assert client.check_token(token.access_token)
    assert token.refresh_token is not None

    refreshed_token = client.refresh_token(token.refresh_token)

    assert client.check_token(refreshed_token.access_token)
    assert token.refresh_token != refreshed_token.refresh_token

    assert client.revoke_token(refreshed_token.access_token).status == "ok"
    assert not client.check_token(refreshed_token.access_token)

    assert client.revoke_token(token.access_token).status == "ok"
    assert not client.check_token(token.access_token)

@pytest.mark.skipif(
    replay_enabled,
    reason="this test has to be explicitly modified to be run outside of replay mode"
)
@pytest.mark.usefixtures("record_or_replay")
def test_device_code_auth(client: yadisk.Client) -> None:
    device_code = client.get_device_code(device_id=device_id)

    with pytest.raises(yadisk.exceptions.AuthorizationPendingError):
        client.get_token_from_device_code(
            device_code.device_code or "",
            device_id=device_id
        )

    token = client.get_token_from_device_code(
        device_code.device_code or "",
        device_id=device_id
    )

    assert client.check_token(token.access_token)

    assert client.revoke_token(token.access_token).status == "ok"
    assert not client.check_token(token.access_token)

@pytest.mark.skipif(
    replay_enabled,
    reason="this test has to be explicitly modified to be run outside of replay mode"
)
@pytest.mark.usefixtures("record_or_replay")
@pytest.mark.anyio
async def test_auth_async(async_client: yadisk.AsyncClient) -> None:
    token = await async_client.get_token(confirmation_code, device_id="test device 123")

    assert await async_client.check_token(token.access_token)
    assert token.refresh_token is not None

    refreshed_token = await async_client.refresh_token(token.refresh_token)

    assert await async_client.check_token(refreshed_token.access_token)

    assert (await async_client.revoke_token(refreshed_token.access_token)).status == "ok"
    assert not await async_client.check_token(refreshed_token.access_token)

    assert (await async_client.revoke_token(refreshed_token.access_token)).status == "ok"
    assert not await async_client.check_token(token.access_token)

@pytest.mark.skipif(
    replay_enabled,
    reason="this test has to be explicitly modified to be run outside of replay mode"
)
@pytest.mark.usefixtures("record_or_replay")
@pytest.mark.anyio
async def test_device_code_auth_async(async_client: yadisk.AsyncClient) -> None:
    device_code = await async_client.get_device_code(device_id=device_id)

    with pytest.raises(yadisk.exceptions.AuthorizationPendingError):
        await async_client.get_token_from_device_code(
            device_code.device_code or "",
            device_id=device_id
        )

    token = await async_client.get_token_from_device_code(
        device_code.device_code or "",
        device_id=device_id
    )

    assert await async_client.check_token(token.access_token)

    assert (await async_client.revoke_token(token.access_token)).status == "ok"
    assert not await async_client.check_token(token.access_token)
