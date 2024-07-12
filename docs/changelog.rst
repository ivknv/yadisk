Changelog
=========

.. _issue #2: https://github.com/ivknv/yadisk/issues/2
.. _issue #4: https://github.com/ivknv/yadisk/issues/4
.. _issue #7: https://github.com/ivknv/yadisk/issues/7
.. _issue #23: https://github.com/ivknv/yadisk/issues/23
.. _issue #26: https://github.com/ivknv/yadisk/issues/26
.. _issue #28: https://github.com/ivknv/yadisk/issues/28
.. _issue #29: https://github.com/ivknv/yadisk/issues/29
.. _PR #31: https://github.com/ivknv/yadisk/pull/31
.. _issue #43: https://github.com/ivknv/yadisk/issues/43
.. _issue #45: https://github.com/ivknv/yadisk/issues/45
.. _issue #49: https://github.com/ivknv/yadisk/issues/49
.. _requests: https://pypi.org/project/requests

.. role:: python(code)
   :language: python

* **Release 3.1.0 (2024-07-12)**

  * New features:

    * Added new exception classes: :any:`GoneError` and
      :any:`ResourceDownloadLimitExceededError`
    * Added a new method: :any:`Client.get_all_public_resources()` and
      :any:`AsyncClient.get_all_public_resources()`
  * Bug fixes:

    * Fixed setting :code:`headers` and session arguments to :code:`None` causing
      errors
    * Fixed incorrect handling of empty filename in :any:`Client.rename()` and
      :any:`AsyncClient.rename()`
    * Fixed several typos in async convenience method implementations
      (:code:`listdir()` and related)
    * Fixed :any:`PublicResourceListObject` having the wrong type for its
      :code:`items` member
    * Fixed API requests not working with :any:`PycURLSession` when
      :code:`stream=True` is set
    * No data will be written to the output file by :any:`Client.download()`,
      :any:`Client.download_by_link()`, :any:`AsyncClient.download()` and
      :any:`AsyncClient.download_by_link()` if the server returns a bad status
      code

* **Release 3.0.1 (2024-07-09)**

  * Fixed broken :code:`pyproject.toml` that did not include full package
    contents (see `issue #49`_)

* **Release 3.0.0 (2024-07-09)**

  * Breaking changes:

    - See :doc:`/migration_guide` for full details
    - All methods wait for asynchronous operations to complete by default
      (see the new :code:`wait=<bool>` parameter)
    - Iterating over the result of :any:`AsyncClient.listdir()` no longer
      requires the additional await keyword.
    - Number of returned items of :any:`Client.get_files()` /
      :any:`AsyncClient.get_files()` is now controlled by the :code:`max_items`
      parameter, rather than :code:`limit`
    - Methods :code:`set_token()`, :code:`set_headers()` of :any:`Session` and
      :any:`AsyncSession` were removed
    - Some methods no longer accept the :code:`fields` parameter
    - :any:`Client.get_last_uploaded()` / :any:`AsyncClient.get_last_uploaded()`
      now return a list instead of a generator
    - :code:`yadisk.api` is now a private module
    - All private modules were renamed to have names that start with :code:`_`
      (e.g, :code:`yadisk._api`)
  * New features:

    - Added methods to wait until an asynchronous operation completes
      (see :any:`Client.wait_for_operation()` / :any:`AsyncClient.wait_for_operation()`)
    - Methods that may start an asynchronous operation now accept additional
      parameters: :python:`wait: bool = True`,
      :python:`poll_interval: float = 1.0` and
      :python:`poll_timeout: Optional[float] = None`
    - :any:`Client.listdir()`, :any:`Client.get_files()` and their async
      variants now accept a new parameter
      :python:`max_items: Optional[int] = None`, which can be used to limit
      the maximum number of returned items
    - Most :any:`Client` and :any:`AsyncClient` methods now accept an optional
      parameter :python:`retry_on: Optional[Tuple[Type[Exception], ...]] = None`,
      which lets you specify a tuple of additional exceptions that can trigger
      an automatic retry
    - :any:`yadisk.types` module is now public
    - Added basic logging of outgoing API requests and automatic retries
    - The logger instance for the library can be accessed as
      :any:`yadisk.settings.logger`
    - Added :any:`YaDiskObject.field()` and the :code:`@` operator
      (:any:`YaDiskObject.__matmul__()`) which verify that the given field is
      not :code:`None`
    - Added :any:`Client.get_upload_link_object()`,
      :any:`AsyncClient.get_upload_link_object()` whose return values
      additionally contain :code:`operation_id`
    - :any:`utils.auto_retry()` now accepts more parameters
    - Added a few missing fields for :any:`DiskInfoObject`
    - :any:`EXIFObject` now contains GPS coordinates
    - :any:`CaseInsensitiveDict` is now part of :any:`yadisk.utils`
  * Improvements:

    - Added full type hints for :any:`Client`, :any:`AsyncClient` through
      :code:`.pyi` stub files
    - Docstrings for :any:`Client` / :any:`AsyncClient` now include more
      parameters
    - Errors during JSON processing (e.g. :any:`InvalidResponseError`) also
      trigger automatic retries
    - Error message when the default session module is not available is now
      less confusing (see `issue #43`_)
    - Reduced :any:`Client.listdir()`'s default :code:`limit` to :code:`500`
      from :code:`10000` to avoid timeouts on large directories (see `issue #45`_)
    - Reduced :any:`Client.get_files()`'s default :code:`limit` to :code:`200`
      from :code:`1000` to avoid timeouts
    - :any:`Client.download()` and similar methods no longer set
      :code:`Connection: close` header, since it's not necessary (unlike with
      :any:`Client.upload()`)
    - :any:`UnknownYaDiskError` now includes status code in the error message
  * Bug fixes:

    - Fixed :code:`httpx`- and :code:`aiohttp`-based session implementations
      not converting their exceptions to :any:`RequestError` in their
      :any:`Response.json()` / :any:`AsyncResponse.json()` implementations
    - Fixed :python:`stream=True` not being set by default in
      :any:`AsyncClient.download()`, :any:`AsyncClient.download_public()`
  * Other changes:

    - :code:`typing_extensions` is now required for Python < 3.10

* **Release 2.1.0 (2024-01-03)**

  * Fixed a bug where POST request parameters were not encoded correctly
  * Fixed a bug in :code:`PycURLSession.send_request()` that made it ignore passed headers
  * :code:`RequestsSession.close()` now closes all underlying session
    instances, instead of only the current thread-local one
  * All methods of :any:`Client` and :any:`AsyncClient` now use existing session
  * Removed :code:`session_factory` attribute and :code:`make_session()` method
    of :any:`Client` and :any:`AsyncClient`
  * Session class can now be specified as a string (see :any:`Client`/:any:`AsyncClient`)
  * Added :any:`Client.get_device_code()`/:any:`AsyncClient.get_device_code()` methods
  * Added :any:`Client.get_token_from_device_code()`/:any:`AsyncClient.get_token_from_device_code()` methods
  * Added missing :code:`redirect_uri` parameter for :any:`Client.get_auth_url()`/:any:`AsyncClient.get_auth_url()`
    and :any:`Client.get_code_url()`/:any:`AsyncClient.get_code_url()`
  * Added support for PKCE parameters for :any:`Client.get_auth_url()`/:any:`AsyncClient.get_auth_url()`,
    :any:`Client.get_code_url()`/:any:`AsyncClient.get_code_url()` and
    :any:`Client.get_token()`/:any:`AsyncClient.get_token()`
  * Added :code:`scope` attribute for :any:`TokenObject`
  * Added new exception classes: :any:`InvalidClientError`, :any:`InvalidGrantError`,
    :any:`AuthorizationPendingError`, :any:`BadVerificationCodeError` and
    :any:`UnsupportedTokenTypeError`

* **Release 2.0.0 (2023-12-12)**

  * The library now provides both synchronous and asynchronous APIs (see
    :doc:`/intro` and :doc:`/api_reference/index`)
  * Multiple HTTP libraries are supported by default (see
    :doc:`/api_reference/sessions` for the full list)
  * It is now possible to add support for any HTTP library (see
    :doc:`/api_reference/session_interface`)
  * `requests`_ is now an optional dependency (although it's still used by
    default for synchronous API)
  * Note that now requests-specific arguments must be passed differently (see :doc:`/api_reference/sessions`)
  * Preferred HTTP client libraries must be explicitly installed now (see :doc:`/intro`)
  * :any:`Client.upload()` and :any:`Client.upload_by_link()` can now accept
    a function that returns an iterator (or a generator) as a payload

* **Release 1.3.4 (2023-10-15)**

  * `upload()` and `download()` (and related) methods can now
    upload/download non-seekable file-like objects (e.g. `stdin` or `stdout`
    when open in binary mode), see `PR #31`_

* **Release 1.3.3 (2023-04-22)**

  * `app:/` paths now work correctly (see `issue #26`_)

* **Release 1.3.2 (2023-03-20)**

  * Fixed `issue #29`_: TypeError: 'type' object is not subscriptable

* **Release 1.3.1 (2023-02-28)**

  * Fixed `issue #28`_: calling `download_public()` with `path` keyword argument raises `TypeError`
  * Fixed `AttributeError` raised when calling `ResourceLinkObject.public_listdir()`

* **Release 1.3.0 (2023-01-30)**

  * Added convenience methods to `...Object` objects (e.g. see `ResourceObject`)
  * Added type hints
  * Improved error checking and response validation
  * Added `InvalidResponseError`, `PayloadTooLargeError`, `UploadTrafficLimitExceededError`
  * Added a few missing fields to `DiskInfoObject` and `SystemFoldersObject`
  * Added `rename()`, `upload_by_link()` and `download_by_link()` methods
  * Added `default_args` field for `YaDisk` object
  * `download()` and `upload()` now return `ResourceLinkObject`
  * Returned `LinkObject` instances have been replaced by more specific subclasses
  * :any:`ConnectionError` now also triggers a retry

* **Release 1.2.19 (2023-01-20)**

  * Fixed incorrect behavior of the fix from 1.2.18 for paths `disk:`
    and `trash:` (only these two).

* **Release 1.2.18 (2023-01-20)**

  * Fixed `issue #26`_: ':' character in filenames causes `BadRequestError`.
    This is due the behavior of Yandex.Disk's REST API itself but is avoided
    on the library level with this fix.

* **Release 1.2.17 (2022-12-11)**

  * Fixed a minor bug which could cause a `ReferenceError`
    (which would not cause a crash, but still show an error message). The bug
    involved using `__del__()` method in `SelfDestructingSession`
    to automatically close the sessions it seems to affect primarily old Python
    versions (such as 3.4).

* **Release 1.2.16 (2022-08-17)**

  * Fixed a bug in `check_token()`: could throw `ForbiddenError` if
    the application lacks necessary permissions (`issue #23`_).

* **Release 1.2.15 (2021-12-31)**

  * Fixed an issue where `http://` links were not recognized as operation links
    (they were assumed to always be `https://`, since all the other
    requests are always HTTPS).
    Occasionally, Yandex.Disk can for some reason return an `http://` link
    to an asynchronous operation instead of `https://`.
    Both links are now recognized correctly and an `https://` version will
    always be used by `get_operation_status()`, regardless of which one
    Yandex.Disk returned.

* **Release 1.2.14 (2019-03-26)**

  * Fixed a `TypeError` in `get_public_*` functions when passing `path` parameter
    (see `issue #7`_)
  * Added `unlimited_autoupload_enabled` attribute for `DiskInfoObject`

* **Release 1.2.13 (2019-02-23)**

  * Added `md5` parameter for `remove()`
  * Added `UserPublicInfoObject`
  * Added `country` attribute for `UserObject`
  * Added `photoslice_time` attribute for `ResourceObject`, `PublicResourceObject`
    and `TrashResourceObject`

* **Release 1.2.12 (2018-10-11)**

  * Fixed `fields` parameter not working properly in `listdir()` (`issue #4`_)

* **Release 1.2.11 (2018-06-30)**

  * Added the missing parameter `sort` for `get_meta()`
  * Added `file` and `antivirus_status` attributes for `ResourceObject`,
    `PublicResourceObject` and `TrashResourceObject`
  * Added `headers` parameter
  * Fixed a typo in `download()` and `download_public()` (`issue #2`_)
  * Removed `*args` parameter everywhere

* **Release 1.2.10 (2018-06-14)**

  * Fixed `timeout=None` behavior. `None` is supposed to mean 'no timeout' but
    in the older versions it was synonymous with the default timeout.

* **Release 1.2.9 (2018-04-28)**

  * Changed the license to LGPLv3 (see `COPYING` and `COPYING.lesser`)
  * Other package info updates

* **Release 1.2.8 (2018-04-17)**

  * Fixed a couple of typos: `PublicResourceListObject.items` and
    `TrashResourceListObject.items` had wrong types
  * Substitute field aliases in `fields` parameter when performing
    API requests (e.g. `embedded` -> `_embedded`)

* **Release 1.2.7 (2018-04-15)**

  * Fixed a file rewinding bug when uploading/downloading files after a retry

* **Release 1.2.6 (2018-04-13)**

  * Now caching `requests` sessions so that open connections
    can be reused (which can significantly speed things up sometimes)
  * Disable `keep-alive` when uploading/downloading files by default

* **Release 1.2.5 (2018-03-31)**

  * Fixed an off-by-one bug in `utils.auto_retry()`
    (which could sometimes result in `AttributeError`)
  * Retry the whole request for `upload()`, `download()` and `download_public()`
  * Set `stream=True` for `download()` and `download_public()`
  * Other minor fixes

* **Release 1.2.4 (2018-02-19)**

  * Fixed `TokenObject` having `exprires_in` instead of `expires_in` (fixed a typo)

* **Release 1.2.3 (2018-01-20)**

  * Fixed a `TypeError` when `WrongResourceTypeError` is raised

* **Release 1.2.2 (2018-01-19)**

  * `refresh_token()` no longer requires a valid or empty token.

* **Release 1.2.1 (2018-01-14)**

  * Fixed auto retries not working. Whoops.

* **Release 1.2.0 (2018-01-14)**

  * Fixed passing `n_retries=0` to `upload()`,
    `download()` and `download_public()`
  * `upload()`, `download()` and `download_public()`
    no longer return anything (see the docs)
  * Added `utils` module (see the docs)
  * Added `RetriableYaDiskError`, `WrongResourceTypeError`,
    `BadGatewayError` and `GatewayTimeoutError`
  * `listdir()` now raises `WrongResourceTypeError`
    instead of `NotADirectoryError`

* **Release 1.1.1 (2017-12-29)**

  * Fixed argument handling in `upload()`, `download()` and `download_public()`.
    Previously, passing `n_retries` and `retry_interval` would raise an exception (`TypeError`).

* **Release 1.1.0 (2017-12-27)**

  * Better exceptions (see the docs)
  * Added support for `force_async` parameter
  * Minor bug fixes

* **Release 1.0.8 (2017-11-29)**

  * Fixed yet another `listdir()` bug

* **Release 1.0.7 (2017-11-04)**

  * Added `install_requires` argument to `setup.py`

* **Release 1.0.6 (2017-11-04)**

  * Return `OperationLinkObject` in some functions

* **Release 1.0.5 (2017-10-29)**

  * Fixed `setup.py` to exclude tests

* **Release 1.0.4 (2017-10-23)**

  * Fixed bugs in `upload`, `download` and `listdir` functions
  * Set default `listdir` `limit` to `10000`

* **Release 1.0.3 (2017-10-22)**

  * Added settings

* **Release 1.0.2 (2017-10-19)**

  * Fixed `get_code_url` function (added missing parameters)

* **Release 1.0.1 (2017-10-18)**

  * Fixed a major bug in `GetTokenRequest` (added missing parameter)

* **Release 1.0.0 (2017-10-18)**

  * Initial release
