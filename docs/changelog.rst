Changelog
=========

.. _issue #2: https://github.com/ivknv/yadisk/issues/2
.. _issue #4: https://github.com/ivknv/yadisk/issues/4
.. _issue #7: https://github.com/ivknv/yadisk/issues/7
.. _issue #23: https://github.com/ivknv/yadisk/issues/23
.. _issue #26: https://github.com/ivknv/yadisk/issues/26
.. _issue #28: https://github.com/ivknv/yadisk/issues/28

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
