# -*- coding: utf-8 -*-
# Copyright © 2024 Ivan Konovalov

# This file is part of a Python library yadisk.

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, see <http://www.gnu.org/licenses/>.

from typing import Optional, Any, Union, Literal, overload
from ._typing_compat import Dict, AsyncGenerator, Iterable, List, Tuple, Type

from .objects import (
    DeviceCodeObject, TokenObject, TokenRevokeStatusObject,
    DiskInfoObject, AsyncResourceObject, AsyncResourceLinkObject,
    AsyncOperationLinkObject, AsyncTrashResourceObject, AsyncPublicResourceObject,
    AsyncPublicResourcesListObject, AsyncPublicResourceLinkObject,
    ResourceUploadLinkObject, PublicAvailableSettingsObject, PublicSettingsObject
)

from .types import (
    AsyncFileOrPath, AsyncFileOrPathDestination, Headers, OperationStatus, AsyncSession,
    AsyncSessionName, AsyncSessionFactory, AsyncOpenFileCallback, TimeoutParameter,
    PublicSettings
)

__all__ = ["AsyncClient"]


class AsyncClient:
    id: str
    secret: str
    token: str
    default_args: Dict[str, Any]
    session: AsyncSession
    open_file: AsyncOpenFileCallback

    synchronous = False

    def __init__(
        self,
        id:     str = "",
        secret: str = "",
        token:  str = "",
        *,
        default_args:    Optional[Dict[str, Any]] = None,
        session:         Optional[Union[AsyncSession, AsyncSessionName]] = None,
        open_file:       Optional[AsyncOpenFileCallback] = None,
        session_factory: Optional[AsyncSessionFactory] = None
    ) -> None:
        ...

    async def __aenter__(self): ...
    async def __aexit__(self, *args, **kwargs) -> None: ...
    async def close(self) -> None: ...

    def get_auth_url(
        self,
        type:                  Union[Literal["code"], Literal["token"]],
        device_id:             Optional[str] = None,
        device_name:           Optional[str] = None,
        redirect_uri:          Optional[str] = None,
        login_hint:            Optional[str] = None,
        scope:                 Optional[str] = None,
        optional_scope:        Optional[str] = None,
        force_confirm:         bool = True,
        state:                 Optional[str] = None,
        code_challenge:        Optional[str] = None,
        code_challenge_method: Optional[Union[Literal["plain"], Literal["S256"]]] = None,
        display:               None = None
    ) -> str:
        ...

    def get_code_url(
        self,
        device_id:             Optional[str] = None,
        device_name:           Optional[str] = None,
        redirect_uri:          Optional[str] = None,
        login_hint:            Optional[str] = None,
        scope:                 Optional[str] = None,
        optional_scope:        Optional[str] = None,
        force_confirm:         bool = True,
        state:                 Optional[str] = None,
        code_challenge:        Optional[str] = None,
        code_challenge_method: Optional[Union[Literal["plain"], Literal["S256"]]] = None,
        display:               None = None
    ) -> str: ...

    async def get_device_code(
        self,
        *,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        scope: Optional[str] = None,
        optional_scope: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> DeviceCodeObject: ...

    async def get_token(
        self,
        code: str,
        /,
        *,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        code_verifier: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> TokenObject:
        ...

    async def get_token_from_device_code(
        self,
        device_code: str,
        /,
        *,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> TokenObject:
        ...

    async def refresh_token(
        self,
        refresh_token: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> TokenObject:
        ...

    async def revoke_token(
        self,
        token: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> TokenRevokeStatusObject:
        ...

    async def check_token(
        self,
        token: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def get_disk_info(
        self,
        *,
        extra_fields: Optional[Iterable[str]] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> DiskInfoObject:
        ...

    async def get_meta(
        self,
        path: str,
        /,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncResourceObject:
        ...

    async def exists(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def get_type(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def is_file(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def is_dir(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def listdir(
        self,
        path: str,
        /,
        *,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncResourceObject, None]:
        # This line here is needed so that the type checker knows that this is
        # an async generator, rather than a simple async function
        yield AsyncResourceObject()

    async def get_upload_link(
        self,
        path: str,
        /,
        *,
        overwrite: bool = False,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def get_upload_link_object(
        self,
        path: str,
        /,
        *,
        overwrite: bool = False,
        fields: Optional[Iterable[str]] = None,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ResourceUploadLinkObject:
        ...

    async def upload(
        self,
        file_or_path: AsyncFileOrPath,
        dst_path: str,
        /,
        *,
        overwrite: bool = False,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncResourceLinkObject:
        ...

    async def upload_by_link(
        self,
        file_or_path: AsyncFileOrPath,
        link: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ...

    async def get_download_link(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def download(
        self,
        src_path: str,
        file_or_path: AsyncFileOrPathDestination,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncResourceLinkObject:
        ...

    async def download_by_link(
        self,
        link: str,
        file_or_path: AsyncFileOrPathDestination,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ...

    @overload
    async def remove(
        self,
        path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        md5: Optional[str] = None,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def remove(
        self,
        path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        md5: Optional[str] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[AsyncOperationLinkObject]:
        ...

    async def mkdir(
        self,
        path: str,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncResourceLinkObject:
        ...

    async def makedirs(
        self,
        path: str,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncResourceLinkObject:
        ...

    async def get_trash_meta(
        self,
        path: str,
        /,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncTrashResourceObject:
        ...

    async def trash_exists(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    @overload
    async def copy(
        self,
        src_path: str,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def copy(
        self,
        src_path: str,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def restore_trash(
        self,
        path: str,
        /,
        dst_path: Optional[str] = None,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def restore_trash(
        self,
        path: str,
        /,
        dst_path: Optional[str] = None,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def move(
        self,
        src_path: str,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def move(
        self,
        src_path: str,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def rename(
        self,
        src_path: str,
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def rename(
        self,
        src_path: str,
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def remove_trash(
        self,
        path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def remove_trash(
        self,
        path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[AsyncOperationLinkObject]:
        ...

    async def publish(
        self,
        path: str,
        /,
        *,
        allow_address_access: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncResourceLinkObject:
        ...

    async def unpublish(
        self,
        path: str,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncResourceLinkObject:
        ...

    async def get_public_settings(
        self,
        path: str,
        /,
        allow_address_access: bool = False,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> PublicSettingsObject:
        ...

    async def get_public_available_settings(
        self,
        path: str,
        /,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> PublicAvailableSettingsObject:
        ...

    async def update_public_settings(
        self,
        path: str,
        public_settings: PublicSettings,
        /,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ...

    @overload
    async def save_to_disk(
        self,
        public_key: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        name: Optional[str] = None,
        path: Optional[str] = None,
        save_path: Optional[str] = None,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def save_to_disk(
        self,
        public_key: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        name: Optional[str] = None,
        path: Optional[str] = None,
        save_path: Optional[str] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    async def get_public_meta(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncPublicResourceObject:
        ...

    async def public_exists(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def public_listdir(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncPublicResourceObject, None]:
        # This line here is needed so that the type checker knows that this is
        # an async generator, rather than a simple async function
        yield AsyncPublicResourceObject()

    async def get_public_type(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def is_public_dir(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def is_public_file(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def trash_listdir(
        self,
        path: str,
        /,
        *,
        limit: Optional[int] = None,
        max_items: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncTrashResourceObject, None]:
        # This line here is needed so that the type checker knows that this is
        # an async generator, rather than a simple async function
        yield AsyncTrashResourceObject()

    async def get_trash_type(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def is_trash_dir(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def is_trash_file(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def get_public_resources(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        type: Optional[Union[Literal["file"], Literal["dir"]]] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncPublicResourcesListObject:
        ...

    async def get_all_public_resources(
        self,
        *,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        type: Optional[Union[Literal["file"], Literal["dir"]]] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncPublicResourceObject, None]:
        yield AsyncPublicResourceObject()

    async def patch(
        self,
        path: str,
        properties: dict,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncResourceObject:
        ...

    async def get_files(
        self,
        *,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        media_type: Optional[Union[str, Iterable[str]]] = None,
        sort: Optional[str] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncResourceObject, None]:
        # This line here is needed so that the type checker knows that this is
        # an async generator, rather than a simple async function
        yield AsyncResourceObject()

    async def get_last_uploaded(
        self,
        *,
        limit: Optional[int] = None,
        media_type: Optional[Union[str, Iterable[str]]] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[AsyncResourceObject]: ...

    async def upload_url(
        self,
        url: str,
        path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        disable_redirects: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    async def get_public_download_link(
        self,
        public_key: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def download_public(
        self,
        public_key: str,
        file_or_path: AsyncFileOrPathDestination,
        /,
        *,
        path: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncPublicResourceLinkObject:
        ...

    async def get_operation_status(
        self,
        operation_id: str,
        /,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> OperationStatus:
        ...

    async def wait_for_operation(
        self,
        operation_id: str,
        /,
        *,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ...
