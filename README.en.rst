YaDisk
======

.. image:: https://img.shields.io/readthedocs/yadisk.svg
   :alt: Read the Docs
   :target: https://yadisk.readthedocs.io/en/latest/
   
.. image:: https://img.shields.io/pypi/v/yadisk.svg
   :alt: PyPI
   :target: https://pypi.org/project/yadisk
   
.. image:: https://img.shields.io/aur/version/python-yadisk.svg
   :alt: AUR
   :target: https://aur.archlinux.org/packages/python-yadisk
   
.. image:: https://img.shields.io/badge/Donate-PayPal-green.svg
   :alt: Donate
   :target: https://paypal.me/encryptandsync

YaDisk is a Yandex.Disk REST API client library.

.. _Read the Docs (EN): http://yadisk.readthedocs.io
.. _Read the Docs (RU): http://yadisk.readthedocs.io/ru/latest

Documentation is available at `Read the Docs (EN)`_ and `Read the Docs (RU)`_ (although it's not complete yet).

Installation
************

.. code:: bash

    pip install yadisk

or

.. code:: bash

    python setup.py install

Examples
********

.. code:: python

    import yadisk

    y = yadisk.YaDisk(token="<token>")
    # or
    # y = yadisk.YaDisk("<application-id>", "<application-secret>", "<token>")

    # Check if the token is valid
    print(y.check_token())

    # Get disk information
    print(y.get_disk_info())

    # Print files and directories at "/some/path"
    print(list(y.listdir("/some/path")))

    # Upload "file_to_upload.txt" to "/destination.txt"
    y.upload("file_to_upload.txt", "/destination.txt")

    # Same thing
    with open("file_to_upload.txt", "rb") as f:
        y.upload(f, "/destination.txt")

    # Download "/some-file-to-download.txt" to "downloaded.txt"
    y.download("/some-file-to-download.txt", "downloaded.txt")

    # Permanently remove "/file-to-remove"
    y.remove("/file-to-remove", permanently=True)

    # Create a new directory at "/test-dir"
    print(y.mkdir("/test-dir"))

Changelog
*********

.. _issue #2: https://github.com/ivknv/yadisk/issues/2

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
    Previously, passing :code:`n_retries` and :code:`retry_interval` would raise an exception (`TypeError`).

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
