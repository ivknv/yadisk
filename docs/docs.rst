Documentation
=============

.. autoclass:: yadisk.YaDisk
   :members:

General parameters
##################

Almost all methods of `YaDisk` (the ones that accept `*args` and `**kwargs`) accept some additional arguments:

* **n_retries** - `int`, maximum number of retries for a request
* **retry_delay** - `float`, delay between retries (in seconds)

`requests` parameters like `timeout`, `proxies`, etc. are also accepted (see `requests.request()`).

This also applies to low-level functions and API request objects as well.

Objects
#######

.. automodule:: yadisk.objects

   .. autoclass:: YaDiskObject
      :members:

   .. autoclass:: ErrorObject
      :members:

.. automodule:: yadisk.objects.auth
   :members:

.. automodule:: yadisk.objects.disk
   :members:

.. automodule:: yadisk.objects.resources
   :members:

.. automodule:: yadisk.objects.operations
   :members:

Low-level API
#############

Functions
*********

.. automodule:: yadisk.functions.auth
   :members:

.. automodule:: yadisk.functions.disk
   :members:

.. automodule:: yadisk.functions.resources
   :members:

.. automodule:: yadisk.functions.operations
   :members:

API request objects
*******************

.. automodule:: yadisk.api

   .. autoclass:: APIRequest
      :members:

.. automodule:: yadisk.api.auth
   :members:

.. automodule:: yadisk.api.disk
   :members:

.. automodule:: yadisk.api.resources
   :members:

.. automodule:: yadisk.api.operations
   :members:
