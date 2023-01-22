
Documentation
=============

.. autoclass:: yadisk.YaDisk
   :members:
   :inherited-members:

General parameters
##################

Almost all methods of `YaDisk` (the ones that accept `**kwargs`) accept some additional arguments:

* **n_retries** - `int`, maximum number of retries for a request
* **retry_interval** - `float`, delay between retries (in seconds)
* **headers** - `dict` or `None`, additional request headers

`requests` parameters like `timeout`, `proxies`, etc. are also accepted (see :py:func:`requests.request`).

This also applies to low-level functions and API request objects as well.

Settings
########

The following settings can be accessed and changed at runtime in `yadisk.settings` module:

* **DEFAULT_TIMEOUT** - `tuple` of 2 numbers (`int` or float`), default timeout for requests. First number is the connect timeout, the second one is the read timeout.
* **DEFAULT_N_RETRIES** - `int`, default number of retries
* **DEFAULT_RETRY_INTERVAL** - `float`, default retry interval
* **DEFAULT_UPLOAD_TIMEOUT** - analogous to `DEFAULT_TIMEOUT` but for `upload` function
* **DEFAULT_UPLOAD_RETRY_INTERVAL** - analogous to `DEFAULT_RETRY_INTERVAL` but for `upload` function

Exceptions
##########

Aside from the exceptions listed below, API requests can also raise exceptions in `requests`.

.. automodule:: yadisk.exceptions
   :members:
   :show-inheritance:

Objects
#######

.. automodule:: yadisk.objects

   .. autoclass:: YaDiskObject
      :members:

   .. autoclass:: ErrorObject
      :members:
      :show-inheritance:

.. automodule:: yadisk.objects.auth
   :members:
   :show-inheritance:

.. automodule:: yadisk.objects.disk
   :members:
   :show-inheritance:

.. automodule:: yadisk.objects.resources
   :members:
   :inherited-members:
   :show-inheritance:
   :exclude-members: import_fields,set_alias,remove_alias,remove_field,set_field_type,set_field_types

.. automodule:: yadisk.objects.operations
   :members:
   :show-inheritance:

Low-level API
#############

Utilities
*********

.. automodule:: yadisk.utils
   :members:

API request objects
*******************

.. automodule:: yadisk.api

   .. autoclass:: APIRequest
      :members:

.. automodule:: yadisk.api.auth
   :members:
   :show-inheritance:

.. automodule:: yadisk.api.disk
   :members:
   :show-inheritance:

.. automodule:: yadisk.api.resources
   :members:
   :show-inheritance:

.. automodule:: yadisk.api.operations
   :members:
   :show-inheritance:
