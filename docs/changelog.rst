Changelog
=========

.. _issue #2: https://github.com/ivknv/yadisk/issues/2

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
