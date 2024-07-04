Migration Guide
===============

Migrating From 2.x to 3.x
#########################

Waiting for asynchronous operations to complete
-----------------------------------------------

Starting with the version 3.0.0, the following methods will automatically
wait for the asynchronous operation to complete:

* :any:`Client.copy()`, :any:`AsyncClient.copy()`
* :any:`Client.move()`, :any:`AsyncClient.move()`
* :any:`Client.remove()`, :any:`AsyncClient.remove()`
* :any:`Client.remove_trash()`, :any:`AsyncClient.remove_trash()`
* :any:`Client.rename()`, :any:`AsyncClient.rename()`
* :any:`Client.restore_trash()`, :any:`AsyncClient.restore_trash()`
* :any:`Client.save_to_disk()`, :any:`AsyncClient.save_to_disk()`
* :any:`Client.upload_url()`, :any:`AsyncClient.upload_url()`.

This new behavior is controlled by the :code:`wait` parameter, which defaults
to :code:`True`. Waiting is performed by repeatedly checking the operation
status (see :any:`Client.get_operation_status()` and
:any:`Client.wait_for_operation()`) and calling :any:`time.sleep` /
:any:`asyncio.sleep`. If this parameter is explicitly set to :code:`False`, no
additional waiting is performed, this matches the old behavior.

.. note::

   If :code:`wait=True` is set, there is a possibility of getting an
   :any:`AsyncOperationFailedError`, though this is very unlikely in practice.

For more details, see documentation for any of the above-mentioned methods.

Iterating over AsyncClient.listdir()
------------------------------------

Iterating over the result of :any:`AsyncClient.listdir()` no longer requires
the additional :code:`await` keyword:

.. code:: python

    async with yadisk.AsyncClient(token=...) as client:
        # yadisk 3.x
        async for resource in client.listdir():
            do_something(resource)

        # yadisk 2.x, no longer valid, will not work
        async for resource in await client.listdir():
            do_something(resource)

Changes with get_files()
------------------------

Before the version 3.0.0, :any:`Client.get_files()` /
:any:`AsyncClient.get_files()` would return up to :code:`limit` files, unless
it was set to :code:`None`, in which case it would return all of them.

Starting with the version 3.0.0, to control the number of returned files,
a new parameter :code:`max_items` is introduced. :code:`limit` only affects
the number of files queried by a single request (requests are sent until
:code:`max_items` files are obtained or end of the list is reached). This new
behavior is consistent with :any:`Client.listdir()` /
:any:`AsyncClient.listdir()`.

get_last_uploaded() returns a list instead of a generator
---------------------------------------------------------

Starting with the version 3.0.0, :any:`Client.get_last_uploaded()` /
:any:`AsyncClient.get_last_uploaded()` return a list of files instead of a
generator.

Changes with the Session interface
----------------------------------

In version 3.0.0, the following methods were removed:

* :code:`Session.set_token()`, :code:`AsyncSession.set_token()`
* :code:`Session.set_headers()`, :code:`AsyncSession.set_headers()`.

Starting with the version 3.0.0, all HTTP headers (including the
:code:`Authorization` header) are explicitly passed to
:any:`Session.send_request()` / :any:`AsyncSession.send_request()`.

Some methods no longer accept the fields parameter
--------------------------------------------------

Prior to version 3.0.0, the following methods used to accept the optional
:code:`fields` parameter:

* :any:`Client.get_operation_status()`, :any:`AsyncClient.get_operation_status()`
* :any:`Client.get_download_link()`, :any:`AsyncClient.get_download_link()`
* :any:`Client.get_public_download_link()`, :any:`AsyncClient.get_public_download_link()`
* :any:`Client.get_upload_link()`, :any:`AsyncClient.get_upload_link()`.

Migrating From 1.x to 2.x
#########################

Merge with yadisk-async
-----------------------

Starting with version 2.0.0, the library provides both synchronous and
asynchronous APIs.

Changes to exception handling
-----------------------------

Starting with version 2.0.0, all exceptions raised by :any:`Client` and
:any:`AsyncClient` are derived from :any:`YaDiskError`. Exceptions from
underlying dependencies (e.g. :code:`requests` or :code:`aiohttp`) are
converted to :any:`RequestError`. A non-exhaustive list of possible exceptions
is provided by the documentation for :any:`Client` and :any:`AsyncClient`.
More details about exceptions are available in documentation for each specific
API method.

requests and aiohttp are optional dependencies
----------------------------------------------

Prior to version 2.0.0, :code:`requests` was listed as a dependency (and
:code:`aiohttp` was listed as a dependency for :code:`yadisk-async`).
:code:`requests` is still used by default but must be explicitly installed.
As for the asynchronous API, :code:`httpx` is used by default, instead of
:code:`aiohttp`. There are now multiple supported HTTP client libraries.

See :doc:`/api_reference/sessions` for a full list of supported HTTP client
libraries and :doc:`/intro` for installation instructions.
