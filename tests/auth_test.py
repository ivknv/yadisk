# -*- coding: utf-8 -*-

import pytest
import yadisk

confirmation_code = "5320215"

@pytest.mark.usefixtures("record_or_replay")
def test_auth(client: yadisk.Client) -> None:
    # Recording data for this test requires human intervention
    # NOTE: If you re-record this test, make sure you change the
    # application secret afterwards and ensure that none of the captured
    # tokens are valid, otherwise you may end up leaking that data

    token = client.get_token(confirmation_code, device_id="test device 123")

    assert client.check_token(token.access_token)
    assert token.refresh_token is not None

    refreshed_token = client.refresh_token(token.refresh_token)

    assert client.check_token(refreshed_token.access_token)
    assert token.refresh_token != refreshed_token.refresh_token

    assert client.revoke_token(refreshed_token.access_token).status == "ok"
    assert not client.check_token(refreshed_token.access_token)

    assert client.revoke_token(token.access_token).status == "ok"
    assert not client.check_token(token.access_token)

@pytest.mark.usefixtures("record_or_replay")
@pytest.mark.anyio
async def test_auth_async(async_client: yadisk.AsyncClient) -> None:
    # Recording data for this test requires human intervention
    # NOTE: If you re-record this test, make sure you change the
    # application secret afterwards and ensure that none of the captured
    # tokens are valid, otherwise you may end up leaking that data

    token = await async_client.get_token(confirmation_code, device_id="test device 123")

    assert await async_client.check_token(token.access_token)
    assert token.refresh_token is not None

    refreshed_token = await async_client.refresh_token(token.refresh_token)

    assert await async_client.check_token(refreshed_token.access_token)

    assert (await async_client.revoke_token(refreshed_token.access_token)).status == "ok"
    assert not await async_client.check_token(refreshed_token.access_token)

    assert (await async_client.revoke_token(refreshed_token.access_token)).status == "ok"
    assert not await async_client.check_token(token.access_token)
