Session Interface
=================

The :any:`Session` and :any:`AsyncSession` are abstract classes that act as adapters
to underlying HTTP client libraries. A session instance is used by :any:`Client`
or :any:`AsyncClient` to perform all the HTTP requests to the Yandex.Disk API.

These interfaces can be implemented to add support for any HTTP library.
For a concrete example, see the source code of any existing implementation
(e.g. :any:`HTTPXSession`).

Synchronous
###########

.. autoclass:: yadisk.Session
   :members:

.. autoclass:: yadisk.Response
   :members:

Asynchronous
############

.. autoclass:: yadisk.AsyncSession
   :members:

.. autoclass:: yadisk.AsyncResponse
   :members:
