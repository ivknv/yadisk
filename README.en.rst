YaDisk
======

.. |RTD Badge| image:: https://img.shields.io/readthedocs/yadisk.svg
   :alt: Read the Docs
   :target: https://yadisk.readthedocs.io/en/latest/

.. |CI Badge| image:: https://img.shields.io/github/actions/workflow/status/ivknv/yadisk/lint_and_test.yml
   :alt: GitHub Actions Workflow Status

.. |PyPI Badge| image:: https://img.shields.io/pypi/v/yadisk.svg
   :alt: PyPI
   :target: https://pypi.org/project/yadisk

.. |Python Version Badge| image:: https://img.shields.io/pypi/pyversions/yadisk
   :alt: PyPI - Python Version

.. |Coverage Badge| image:: https://coveralls.io/repos/github/ivknv/yadisk/badge.svg?branch=master
   :alt: Coverage
   :target: https://coveralls.io/github/ivknv/yadisk

|RTD Badge| |CI Badge| |PyPI Badge| |Python Version Badge| |Coverage Badge|

YaDisk is a Yandex.Disk REST API client library.

.. _Read the Docs (EN): https://yadisk.readthedocs.io
.. _Read the Docs (RU): https://yadisk.readthedocs.io/ru/latest

Documentation is available at `Read the Docs (EN)`_ and `Read the Docs (RU)`_.

.. contents:: Table of contents:

Installation
************

:code:`yadisk` supports multiple HTTP client libraries and has both synchronous and
asynchronous API.

The following HTTP client libraries are currently supported:

* :code:`requests` (used by default for synchronous API)
* :code:`httpx` (both synchronous and asynchronous, used by default for asynchronous API)
* :code:`aiohttp` (asynchronous only)
* :code:`pycurl` (synchronous only)

For synchronous API (installs :code:`requests`):

.. code:: bash

   pip install yadisk[sync-defaults]

For asynchronous API (installs :code:`aiofiles` and :code:`httpx`):

.. code:: bash

   pip install yadisk[async-defaults]

Alternatively, you can manually choose which optional libraries to install:

.. code:: bash

   # For use with pycurl
   pip install yadisk[pycurl]

   # For use with aiohttp, will also install aiofiles
   pip install yadisk[async-files,aiofiles]

Examples
********

Synchronous API
---------------

.. code:: python

    import yadisk

    client = yadisk.Client(token="<token>")
    # or
    # client = yadisk.Client("<application-id>", "<application-secret>", "<token>")

    # You can either use the with statement or manually call client.close() later
    with client:
        # Check if the token is valid
        print(client.check_token())

        # Get disk information
        print(client.get_disk_info())

        # Print files and directories at "/some/path"
        print(list(client.listdir("/some/path")))

        # Upload "file_to_upload.txt" to "/destination.txt"
        client.upload("file_to_upload.txt", "/destination.txt")

        # Same thing
        with open("file_to_upload.txt", "rb") as f:
            client.upload(f, "/destination.txt")

        # Download "/some-file-to-download.txt" to "downloaded.txt"
        client.download("/some-file-to-download.txt", "downloaded.txt")

        # Permanently remove "/file-to-remove"
        client.remove("/file-to-remove", permanently=True)

        # Create a new directory at "/test-dir"
        print(client.mkdir("/test-dir"))

Asynchronous API
----------------

.. code:: python

    import yadisk
    import aiofiles

    client = yadisk.AsyncClient(token="<token>")
    # or
    # client = yadisk.AsyncClient("<application-id>", "<application-secret>", "<token>")

    # You can either use the with statement or manually call client.close() later
    async with client:
        # Check if the token is valid
        print(await client.check_token())

        # Get disk information
        print(await client.get_disk_info())

        # Print files and directories at "/some/path"
        print([i async for i in client.listdir("/some/path")])

        # Upload "file_to_upload.txt" to "/destination.txt"
        await client.upload("file_to_upload.txt", "/destination.txt")

        # Same thing
        async with aiofiles.open("file_to_upload.txt", "rb") as f:
            await client.upload(f, "/destination.txt")

        # Same thing but with regular files
        with open("file_to_upload.txt", "rb") as f:
            await client.upload(f, "/destination.txt")

        # Download "/some-file-to-download.txt" to "downloaded.txt"
        await client.download("/some-file-to-download.txt", "downloaded.txt")

        # Same thing
        async with aiofiles.open("downloaded.txt", "wb") as f:
            await client.download("/some-file-to-download.txt", f)

        # Permanently remove "/file-to-remove"
        await client.remove("/file-to-remove", permanently=True)

        # Create a new directory at "/test-dir"
        print(await client.mkdir("/test-dir"))

Contributing
************

If you would like to contribute to this project, see
`CONTRIBUTING.rst <https://github.com/ivknv/yadisk/blob/master/CONTRIBUTING.rst>`_.

Changelog
*********

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
.. _issue #53: https://github.com/ivknv/yadisk/issues/53
.. _Introduction: https://yadisk.readthedocs.io/en/latest/intro.html
.. _API Reference: https://yadisk.readthedocs.io/en/latest/api_reference/index.html
.. _Available Session Implementations: https://yadisk.readthedocs.io/en/latest/api_reference/sessions.html
.. _Session Interface: https://yadisk.readthedocs.io/en/latest/api_reference/session_interface.html
.. _requests: https://pypi.org/project/requests
.. _Migration Guide: https://yadisk.readthedocs.io/en/latest/migration_guide.html
.. _PR #57: https://github.com/ivknv/yadisk/pull/57

* **Release 3.4.0 (2025-07-10)**

  * New features:

    * Added methods for managing public settings of resources:

      * :code:`Client.update_public_settings()`
      * :code:`Client.get_public_settings()`
      * :code:`Client.get_public_available_settings()`

      Note, it appears that these API endpoints do not fully conform to the
      official REST API documentation, their functionality is limited in
      practice.

    * Added new exception class :code:`PasswordRequiredError`

    * Added several new fields for :code:`DiskInfoObject`:

      * :code:`deletion_restricion_days`
      * :code:`hide_screenshots_in_photoslice`
      * :code:`is_legal_entity`

    * Implemented the :code:`__dir__()` method for response objects

  * Improvements:

    * :code:`repr()` of API response objects now only shows the keys that are
      actually present (instead of displaying them as :code:`None` like before)

* **Release 3.3.0 (2025-04-29)**

  * New features:

    * User-Agent spoofing to bypass Yandex.Disk's upload speed limit (see `PR #57`_).
      :code:`Client.upload()` and related methods (including :code:`AsyncClient`)
      have a new optional parameter :code:`spoof_user_agent`, which is set to
      :code:`True` by default. This parameter can be used to disable User-Agent
      spoofing if necessary.

    * Added IPython's pretty printing support for :code:`YaDiskObject` and
      derived classes

  * Bug fixes:

    * :code:`Client.wait_for_operation()` now uses :code:`time.monotonic()`
      instead of :code:`time.time()`

  * Improvements:

    * REST API error messages are now clearly divided into four parts (message,
      description, error code and HTTP status code)

* **Release 3.2.0 (2025-02-03)**

  * New features:

    * Added new method: :code:`Client.makedirs()` / :code:`AsyncClient.makedirs()`
      (see `issue #53`_)
    * Added several missing fields for :code:`DiskInfoObject`:

      * :code:`photounlim_size`
      * :code:`will_be_overdrawn`
      * :code:`free_photounlim_end_date`
      * :code:`payment_flow`

    * Added missing field :code:`sizes` for :code:`ResourceObject` and related
      objects

  * Bug fixes:

    * :code:`Client.rename()` / :code:`AsyncClient.rename()` now raises
      :code:`ValueError` on attempt to rename the root directory
    * Automatic retry attempt numbers were logged off by one, now they are
      logged correctly

* **Release 3.1.0 (2024-07-12)**

  * New features:

    * Added new exception classes: :code:`GoneError` and
      :code:`ResourceDownloadLimitExceededError`
    * Added a new method: :code:`Client.get_all_public_resources()` and
      :code:`AsyncClient.get_all_public_resources()`
  * Bug fixes:

    * Fixed setting :code:`headers` and session arguments to :code:`None` causing
      errors
    * Fixed incorrect handling of empty filename in :code:`Client.rename()` and
      :code:`AsyncClient.rename()`
    * Fixed several typos in async convenience method implementations
      (:code:`listdir()` and related)
    * Fixed :code:`PublicResourceListObject` having the wrong type for its
      :code:`items` member
    * Fixed API requests not working with :code:`PycURLSession` when
      :code:`stream=True` is set
    * No data will be written to the output file by :code:`Client.download()`,
      :code:`Client.download_by_link()`, :code:`AsyncClient.download()` and
      :code:`AsyncClient.download_by_link()` if the server returns a bad status
      code

* **Release 3.0.1 (2024-07-09)**

  * Fixed broken :code:`pyproject.toml` that did not include full package
    contents (see `issue #49`_)

* **Release 3.0.0 (2024-07-09)**

  * Breaking changes:

    - See `Migration Guide`_ for full details
    - All methods wait for asynchronous operations to complete by default
      (see the new :code:`wait=<bool>` parameter)
    - Iterating over the result of :code:`AsyncClient.listdir()` no longer
      requires the additional await keyword.
    - Number of returned items of :code:`Client.get_files()` /
      :code:`AsyncClient.get_files()` is now controlled by the :code:`max_items`
      parameter, rather than :code:`limit`
    - Methods :code:`set_token()`, :code:`set_headers()` of :code:`Session` and
      :code:`AsyncSession` were removed
    - Some methods no longer accept the :code:`fields` parameter
    - :code:`Client.get_last_uploaded()` / :code:`AsyncClient.get_last_uploaded()`
      now return a list instead of a generator
    - :code:`yadisk.api` is now a private module
    - All private modules were renamed to have names that start with :code:`_`
      (e.g, :code:`yadisk._api`)
  * New features:

    - Added methods to wait until an asynchronous operation completes
      (see :code:`Client.wait_for_operation()` / :code:`AsyncClient.wait_for_operation()`)
    - Methods that may start an asynchronous operation now accept additional
      parameters: :code:`wait: bool = True`,
      :code:`poll_interval: float = 1.0` and
      :code:`poll_timeout: Optional[float] = None`
    - :code:`Client.listdir()`, :code:`Client.get_files()` and their async
      variants now accept a new parameter
      :code:`max_items: Optional[int] = None`, which can be used to limit
      the maximum number of returned items
    - Most :code:`Client` and :code:`AsyncClient` methods now accept an optional
      parameter :code:`retry_on: Optional[Tuple[Type[Exception], ...]] = None`,
      which lets you specify a tuple of additional exceptions that can trigger
      an automatic retry
    - :code:`yadisk.types` module is now public
    - Added basic logging of outgoing API requests and automatic retries
    - The logger instance for the library can be accessed as
      :code:`yadisk.settings.logger`
    - Added :code:`YaDiskObject.field()` and the :code:`@` operator
      (:code:`YaDiskObject.__matmul__()`) which verify that the given field is
      not :code:`None`
    - Added :code:`Client.get_upload_link_object()`,
      :code:`AsyncClient.get_upload_link_object()` whose return values
      additionally contain :code:`operation_id`
    - :code:`utils.auto_retry()` now accepts more parameters
    - Added a few missing fields for :code:`DiskInfoObject`
    - :code:`EXIFObject` now contains GPS coordinates
    - :code:`CaseInsensitiveDict` is now part of :code:`yadisk.utils`
  * Improvements:

    - Added full type hints for :code:`Client`, :code:`AsyncClient` through
      :code:`.pyi` stub files
    - Docstrings for :code:`Client` / :code:`AsyncClient` now include more
      parameters
    - Errors during JSON processing (e.g. :code:`InvalidResponseError`) also
      trigger automatic retries
    - Error message when the default session module is not available is now
      less confusing (see `issue #43`_)
    - Reduced :code:`Client.listdir()`'s default :code:`limit` to :code:`500`
      from :code:`10000` to avoid timeouts on large directories (see `issue #45`_)
    - Reduced :code:`Client.get_files()`'s default :code:`limit` to :code:`200`
      from :code:`1000` to avoid timeouts
    - :code:`Client.download()` and similar methods no longer set
      :code:`Connection: close` header, since it's not necessary (unlike with
      :code:`Client.upload()`)
    - :code:`UnknownYaDiskError` now includes status code in the error message
  * Bug fixes:

    - Fixed :code:`httpx`- and :code:`aiohttp`-based session implementations
      not converting their exceptions to :code:`RequestError` in their
      :code:`Response.json()` / :code:`AsyncResponse.json()` implementations
    - Fixed :code:`stream=True` not being set by default in
      :code:`AsyncClient.download()`, :code:`AsyncClient.download_public()`
  * Other changes:

    - :code:`typing_extensions` is now required for Python < 3.10


* **Release 2.1.0 (2024-01-03)**

  * Fixed a bug where POST request parameters were not encoded correctly
  * Fixed a bug in :code:`PycURLSession.send_request()` that made it ignore passed headers
  * :code:`RequestsSession.close()` now closes all underlying session
    instances, instead of only the current thread-local one
  * All methods of :code:`Client` and :code:`AsyncClient` now use existing session
  * Removed :code:`session_factory` attribute and :code:`make_session()` method
    of :code:`Client` and :code:`AsyncClient`
  * Session class can now be specified as a string
  * Added :code:`Client.get_device_code()`/:code:`AsyncClient.get_device_code()` methods
  * Added :code:`Client.get_token_from_device_code()`/:code:`AsyncClient.get_token_from_device_code()` methods
  * Added missing :code:`redirect_uri` parameter for :code:`Client.get_auth_url()`/:code:`AsyncClient.get_auth_url()`
    and :code:`Client.get_code_url()`/:code:`AsyncClient.get_code_url()`
  * Added support for PKCE parameters for :code:`Client.get_auth_url()`/:code:`AsyncClient.get_auth_url()`,
    :code:`Client.get_code_url()`/:code:`AsyncClient.get_code_url()` and
    :code:`Client.get_token()`/:code:`AsyncClient.get_token()`
  * Added :code:`scope` attribute for :code:`TokenObject`
  * Added new exception classes: :code:`InvalidClientError`, :code:`InvalidGrantError`,
    :code:`AuthorizationPendingError`, :code:`BadVerificationCodeError` and
    :code:`UnsupportedTokenTypeError`

* **Release 2.0.0 (2023-12-12)**

  * The library now provides both synchronous and asynchronous APIs (see
    `Introduction`_ and `API Reference`_)
  * Multiple HTTP libraries are supported by default (see
    `Available Session Implementations`_ for the full list)
  * It is now possible to add support for any HTTP library (see
    `Session Interface`_)
  * `requests`_ is now an optional dependency (although it's still used by
    default for synchronous API)
  * Note that now requests-specific arguments must be passed differently
    (see `Available Session Implementations`_)
  * Preferred HTTP client libraries must be explicitly installed now
    (see `Introduction`_)
  * :code:`Client.upload()` and :code:`Client.upload_by_link()` can now accept
    a function that returns an iterator (or a generator) as a payload

* **Release 1.3.4 (2023-10-15)**

  * :code:`upload()` and :code:`download()` (and related) methods can now
    upload/download non-seekable file-like objects (e.g. :code:`stdin` or :code:`stdout`
    when open in binary mode), see `PR #31`_

* **Release 1.3.3 (2023-04-22)**

  * :code:`app:/` paths now work correctly (see `issue #26`_)

* **Release 1.3.2 (2023-03-20)**

  * Fixed `issue #29`_: TypeError: 'type' object is not subscriptable

* **Release 1.3.1 (2023-02-28)**

  * Fixed `issue #28`_: calling :code:`download_public()` with :code:`path` keyword argument raises :code:`TypeError`
  * Fixed :code:`AttributeError` raised when calling :code:`ResourceLinkObject.public_listdir()`

* **Release 1.3.0 (2023-01-30)**

  * Added convenience methods to :code:`...Object` objects (e.g. see :code:`ResourceObject` in docs)
  * Added type hints
  * Improved error checking and response validation
  * Added :code:`InvalidResponseError`, :code:`PayloadTooLargeError`, :code:`UploadTrafficLimitExceededError`
  * Added a few missing fields to :code:`DiskInfoObject` and :code:`SystemFoldersObject`
  * Added :code:`rename()`, :code:`upload_by_link()` and :code:`download_by_link()` methods
  * Added :code:`default_args` field for :code:`YaDisk` object
  * :code:`download()` and :code:`upload()` now return :code:`ResourceLinkObject`
  * Returned :code:`LinkObject` instances have been replaced by more specific subclasses
  * :code:`ConnectionError` now also triggers a retry

* **Release 1.2.19 (2023-01-20)**

  * Fixed incorrect behavior of the fix from 1.2.18 for paths :code:`disk:`
    and :code:`trash:` (only these two).

* **Release 1.2.18 (2023-01-20)**

  * Fixed `issue #26`_: ':' character in filenames causes :code:`BadRequestError`.
    This is due the behavior of Yandex.Disk's REST API itself but is avoided
    on the library level with this fix.

* **Release 1.2.17 (2022-12-11)**

  * Fixed a minor bug which could cause a :code:`ReferenceError`
    (which would not cause a crash, but still show an error message). The bug
    involved using :code:`__del__()` method in :code:`SelfDestructingSession`
    to automatically close the sessions it seems to affect primarily old Python
    versions (such as 3.4).

* **Release 1.2.16 (2022-08-17)**

  * Fixed a bug in :code:`check_token()`: could throw :code:`ForbiddenError` if
    the application lacks necessary permissions (`issue #23`_).

* **Release 1.2.15 (2021-12-31)**

  * Fixed an issue where :code:`http://` links were not recognized as operation links
    (they were assumed to always be :code:`https://`, since all the other
    requests are always HTTPS).
    Occasionally, Yandex.Disk can for some reason return an :code:`http://` link
    to an asynchronous operation instead of :code:`https://`.
    Both links are now recognized correctly and an :code:`https://` version will
    always be used by :code:`get_operation_status()`, regardless of which one
    Yandex.Disk returned.

* **Release 1.2.14 (2019-03-26)**

  * Fixed a :code:`TypeError` in :code:`get_public_*` functions when passing :code:`path` parameter
    (see `issue #7`_)
  * Added :code:`unlimited_autoupload_enabled` attribute for :code:`DiskInfoObject`

* **Release 1.2.13 (2019-02-23)**

  * Added :code:`md5` parameter for :code:`remove()`
  * Added :code:`UserPublicInfoObject`
  * Added :code:`country` attribute for :code:`UserObject`
  * Added :code:`photoslice_time` attribute for :code:`ResourceObject`, :code:`PublicResourceObject`
    and :code:`TrashResourceObject`

* **Release 1.2.13 (2019-02-23)**

  * Added :code:`md5` parameter for :code:`remove()`
  * Added :code:`UserPublicInfoObject`
  * Added :code:`country` attribute for :code:`UserObject`
  * Added :code:`photoslice_time` attribute for :code:`ResourceObject`, :code:`PublicResourceObject`
    and :code:`TrashResourceObject`

* **Release 1.2.12 (2018-10-11)**

  * Fixed `fields` parameter not working properly in `listdir()` (`issue #4`_)

* **Release 1.2.11 (2018-06-30)**

  * Added the missing parameter :code:`sort` for :code:`get_meta()`
  * Added :code:`file` and :code:`antivirus_status` attributes for :code:`ResourceObject`,
    :code:`PublicResourceObject` and :code:`TrashResourceObject`
  * Added :code:`headers` parameter
  * Fixed a typo in :code:`download()` and :code:`download_public()` (`issue #2`_)
  * Removed :code:`*args` parameter everywhere

* **Release 1.2.10 (2018-06-14)**

  * Fixed :code:`timeout=None` behavior. :code:`None` is supposed to mean 'no timeout' but
    in the older versions it was synonymous with the default timeout.

* **Release 1.2.9 (2018-04-28)**

  * Changed the license to LGPLv3 (see :code:`COPYING` and :code:`COPYING.lesser`)
  * Other package info updates

* **Release 1.2.8 (2018-04-17)**

  * Fixed a couple of typos: :code:`PublicResourceListObject.items` and
    :code:`TrashResourceListObject.items` had wrong types
  * Substitute field aliases in :code:`fields` parameter when performing
    API requests (e.g. :code:`embedded` -> :code:`_embedded`)

* **Release 1.2.7 (2018-04-15)**

  * Fixed a file rewinding bug when uploading/downloading files after a retry

* **Release 1.2.6 (2018-04-13)**

  * Now caching :code:`requests` sessions so that open connections
    can be reused (which can significantly speed things up sometimes)
  * Disable :code:`keep-alive` when uploading/downloading files by default

* **Release 1.2.5 (2018-03-31)**

  * Fixed an off-by-one bug in :code:`utils.auto_retry()`
    (which could sometimes result in :code:`AttributeError`)
  * Retry the whole request for :code:`upload()`, :code:`download()` and :code:`download_public()`
  * Set :code:`stream=True` for :code:`download()` and :code:`download_public()`
  * Other minor fixes

* **Release 1.2.4 (2018-02-19)**

  * Fixed :code:`TokenObject` having :code:`exprires_in` instead of :code:`expires_in` (fixed a typo)

* **Release 1.2.3 (2018-01-20)**

  * Fixed a :code:`TypeError` when :code:`WrongResourceTypeError` is raised

* **Release 1.2.2 (2018-01-19)**

  * :code:`refresh_token()` no longer requires a valid or empty token.

* **Release 1.2.1 (2018-01-14)**

  * Fixed auto retries not working. Whoops.

* **Release 1.2.0 (2018-01-14)**

  * Fixed passing :code:`n_retries=0` to :code:`upload()`,
    :code:`download()` and :code:`download_public()`
  * :code:`upload()`, :code:`download()` and :code:`download_public()`
    no longer return anything (see the docs)
  * Added :code:`utils` module (see the docs)
  * Added :code:`RetriableYaDiskError`, :code:`WrongResourceTypeError`,
    :code:`BadGatewayError` and :code:`GatewayTimeoutError`
  * :code:`listdir()` now raises :code:`WrongResourceTypeError`
    instead of :code:`NotADirectoryError`

* **Release 1.1.1 (2017-12-29)**

  * Fixed argument handling in :code:`upload()`, :code:`download()` and :code:`download_public()`.
    Previously, passing :code:`n_retries` and :code:`retry_interval` would raise an exception (:code:`TypeError`).

* **Release 1.1.0 (2017-12-27)**

  * Better exceptions (see the docs)
  * Added support for :code:`force_async` parameter
  * Minor bug fixes

* **Release 1.0.8 (2017-11-29)**

  * Fixed yet another :code:`listdir()` bug

* **Release 1.0.7 (2017-11-04)**

  * Added :code:`install_requires` argument to :code:`setup.py`

* **Release 1.0.6 (2017-11-04)**

  * Return :code:`OperationLinkObject` in some functions

* **Release 1.0.5 (2017-10-29)**

  * Fixed :code:`setup.py` to exclude tests

* **Release 1.0.4 (2017-10-23)**

  * Fixed bugs in :code:`upload`, :code:`download` and :code:`listdir` functions
  * Set default :code:`listdir` :code:`limit` to :code:`10000`

* **Release 1.0.3 (2017-10-22)**

  * Added settings

* **Release 1.0.2 (2017-10-19)**

  * Fixed :code:`get_code_url` function (added missing parameters)

* **Release 1.0.1 (2017-10-18)**

  * Fixed a major bug in :code:`GetTokenRequest` (added missing parameter)

* **Release 1.0.0 (2017-10-18)**

  * Initial release
