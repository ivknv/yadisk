# -*- coding: utf-8 -*-

import pytest
import yadisk

@pytest.mark.anyio
async def test_auto_retry() -> None:
    attempt_counter = 0

    class CustomException(Exception):
        pass

    def attempt() -> None:
        nonlocal attempt_counter

        attempt_counter += 1

        if attempt_counter == 1:
            raise yadisk.exceptions.RequestError("test")
        elif attempt_counter == 2:
            raise yadisk.exceptions.YaDiskConnectionError("test")
        elif attempt_counter == 3:
            raise yadisk.exceptions.InternalServerError(msg="test")
        elif attempt_counter == 4:
            raise yadisk.exceptions.RetriableYaDiskError(msg="test")
        elif attempt_counter == 5:
            raise CustomException("test")

    with pytest.raises(CustomException):
        yadisk.utils.auto_retry(attempt, n_retries=10, retry_interval=0.0)

    assert attempt_counter == 5
    attempt_counter = 0

    with pytest.raises(CustomException):
        await yadisk.utils.async_auto_retry(attempt, n_retries=10, retry_interval=0.0)

    assert attempt_counter == 5
    attempt_counter = 0

    with pytest.raises(yadisk.exceptions.InternalServerError):
        yadisk.utils.auto_retry(attempt, n_retries=2, retry_interval=0.0)

    assert attempt_counter == 3
    attempt_counter = 0

    with pytest.raises(yadisk.exceptions.InternalServerError):
        await yadisk.utils.async_auto_retry(attempt, n_retries=2, retry_interval=0.0)

    assert attempt_counter == 3
    attempt_counter = 0

    yadisk.utils.auto_retry(attempt, n_retries=10, retry_interval=0.0, retry_on=(CustomException,))
    assert attempt_counter == 6
    attempt_counter = 0

    await yadisk.utils.async_auto_retry(attempt, n_retries=10, retry_interval=0.0, retry_on=(CustomException,))
    assert attempt_counter == 6


@pytest.mark.anyio
async def test_auto_retry_with_disable_retries() -> None:
    attempt_counter = 0

    def attempt() -> None:
        nonlocal attempt_counter

        attempt_counter += 1

        if attempt_counter == 1:
            raise yadisk.exceptions.RequestError("test", disable_retry=True)

    with pytest.raises(yadisk.exceptions.RequestError):
        yadisk.utils.auto_retry(attempt, n_retries=5, retry_interval=0.0)

    assert attempt_counter == 1
    attempt_counter = 0

    with pytest.raises(yadisk.exceptions.RequestError):
        await yadisk.utils.async_auto_retry(attempt, n_retries=5, retry_interval=0.0)

    assert attempt_counter == 1


@pytest.mark.anyio
async def test_auto_retry_without_errors() -> None:
    attempt_counter = 0

    def attempt() -> None:
        nonlocal attempt_counter
        attempt_counter += 1

    yadisk.utils.auto_retry(attempt, n_retries=5, retry_interval=0.0)
    assert attempt_counter == 1

    await yadisk.utils.async_auto_retry(attempt, n_retries=5, retry_interval=0.0)
    assert attempt_counter == 2
