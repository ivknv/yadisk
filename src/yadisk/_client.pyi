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

from typing import Optional, Any, Union, Literal
from ._typing_compat import Dict, Generator, Iterable

from .objects import (
    DeviceCodeObject, TokenObject, TokenRevokeStatusObject,
    DiskInfoObject, SyncResourceObject, SyncResourceLinkObject,
    SyncOperationLinkObject, SyncTrashResourceObject, SyncPublicResourceObject,
    SyncPublicResourcesListObject, SyncPublicResourceLinkObject
)

from .types import (
    FileOrPath, FileOrPathDestination, Headers, OperationStatus, Session,
    SessionName, SessionFactory, OpenFileCallback, TimeoutParameter,
    unspecified
)

__all__ = ["Client"]

class Client:
    id: str
    secret: str
    token: str
    default_args: Dict[str, Any]
    session: Session
    open_file: OpenFileCallback

    synchronous = True

    def __init__(
        self,
        id:     str = "",
        secret: str = "",
        token:  str = "",
        *,
        default_args:    Optional[Dict[str, Any]] = None,
        session:         Optional[Union[Session, SessionName]] = None,
        open_file:       Optional[OpenFileCallback] = None,
        session_factory: Optional[SessionFactory] = None
    ) -> None:
        ...

    def __enter__(self): ...
    def __exit__(self, *args, **kwargs) -> None: ...
    def close(self) -> None: ...

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

    def get_device_code(
        self,
        *,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        scope: Optional[str] = None,
        optional_scope: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> DeviceCodeObject: ...

    def get_token(
        self,
        code: str,
        /,
        *,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        code_verifier: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> TokenObject:
        ...

    def get_token_from_device_code(
        self,
        device_code: str,
        /,
        *,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> TokenObject:
        ...

    def refresh_token(
        self,
        refresh_token: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> TokenObject:
        ...

    def revoke_token(
        self,
        token: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> TokenRevokeStatusObject:
        ...

    def check_token(
        self,
        token: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def get_disk_info(
        self,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> DiskInfoObject:
        ...

    def get_meta(
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
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceObject:
        ...

    def exists(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def get_type(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    def is_file(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def is_dir(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def listdir(
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
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Generator[SyncResourceObject, None, None]:
        ...

    def get_upload_link(
        self,
        path: str,
        /,
        *,
        overwrite: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    def upload(
        self,
        file_or_path: FileOrPath,
        dst_path: str,
        /,
        *,
        overwrite: bool = False,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceLinkObject:
        ...

    def upload_by_link(
        self,
        file_or_path: FileOrPath,
        link: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> None:
        ...

    def get_download_link(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    def download(
        self,
        src_path: str,
        file_or_path: FileOrPathDestination,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceLinkObject:
        ...

    def download_by_link(
        self,
        link: str,
        file_or_path: FileOrPathDestination,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> None:
        ...

    def remove(
        self,
        path: str,
        /,
        *,
        md5: Optional[str] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Optional[SyncOperationLinkObject]:
        ...

    def mkdir(
        self,
        path: str,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceLinkObject:
        ...

    def get_trash_meta(
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
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncTrashResourceObject:
        ...

    def trash_exists(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def copy(
        self,
        src_path: str,
        dst_path: str,
        /,
        *,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    def restore_trash(
        self,
        path: str,
        /,
        dst_path: Optional[str] = None,
        *,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    def move(
        self,
        src_path: str,
        dst_path: str,
        /,
        *,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    def rename(
        self,
        src_path: str,
        new_name: str,
        /,
        *,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    def remove_trash(
        self,
        path: str,
        /,
        *,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Optional[SyncOperationLinkObject]:
        ...

    def publish(
        self,
        path: str,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceLinkObject:
        ...

    def unpublish(
        self,
        path: str,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceLinkObject:
        ...

    def save_to_disk(
        self,
        public_key: str,
        /,
        *,
        name: Optional[str] = None,
        path: Optional[str] = None,
        save_path: Optional[str] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    def get_public_meta(
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
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncPublicResourceObject:
        ...

    def public_exists(
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
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def public_listdir(
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
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Generator[SyncPublicResourceObject, None, None]:
        ...

    def get_public_type(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    def is_public_dir(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def is_public_file(
        self,
        public_key: str,
        /,
        *,
        path: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def trash_listdir(
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
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Generator[SyncTrashResourceObject, None, None]:
        ...

    def get_trash_type(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    def is_trash_dir(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def is_trash_file(
        self,
        path: str,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def get_public_resources(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        type: Optional[Union[Literal["file"], Literal["dir"]]] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncPublicResourcesListObject:
        ...

    def patch(
        self,
        path: str,
        properties: dict,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceObject:
        ...

    def get_files(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        media_type: Optional[Union[str, Iterable[str]]] = None,
        sort: Optional[str] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Generator[SyncResourceObject, None, None]:
        ...

    def get_last_uploaded(
        self,
        *,
        limit: Optional[int] = None,
        media_type: Optional[Union[str, Iterable[str]]] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Generator[SyncResourceObject, None, None]:
        ...

    def upload_url(
        self,
        url: str,
        path: str,
        /,
        *,
        disable_redirects: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    def get_public_download_link(
        self,
        public_key: str,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    def download_public(
        self,
        public_key: str,
        file_or_path: FileOrPathDestination,
        /,
        *,
        path: Optional[str] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncPublicResourceLinkObject:
        ...

    def get_operation_status(
        self,
        operation_id: str,
        /,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = unspecified,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> OperationStatus:
        ...