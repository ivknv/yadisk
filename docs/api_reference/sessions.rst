Available Session Implementations
=================================

You can choose which HTTP library will be used by :any:`Client` and :any:`AsyncClient`
by specifying the :code:`session` parameter.
Below you can see the list of session implementations that are shipped with the :code:`yadisk` library.

Alternatively, you can make your own :any:`Session`/:any:`AsyncSession` implementation.
For a concrete example, take a look at the source code of any existing implementations (e.g. :any:`HTTPXSession`).

Synchronous Implementations
###########################

.. autoclass:: yadisk.sessions.requests_session.RequestsSession
   :show-inheritance:

.. autoclass:: yadisk.sessions.httpx_session.HTTPXSession
   :show-inheritance:

.. autoclass:: yadisk.sessions.pycurl_session.PycURLSession
   :show-inheritance:

Asynchronous Implementations
############################

.. autoclass:: yadisk.sessions.aiohttp_session.AIOHTTPSession
   :show-inheritance:

.. autoclass:: yadisk.sessions.async_httpx_session.AsyncHTTPXSession
   :show-inheritance:
