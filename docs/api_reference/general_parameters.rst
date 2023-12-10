General Parameters
==================

Almost all methods of :any:`Client` (the ones that accept `**kwargs`) accept some additional arguments:

* **n_retries** - `int`, maximum number of retries for a request
* **retry_interval** - `float`, delay between retries (in seconds)
* **headers** - `dict` or `None`, additional request headers
* **timeout** - `tuple` (:code:`(<connect timeout>, <read timeout>)`) or `float` (specifies both connect and read timeout), request timeout (in seconds)

Additional parameters, specific to a given HTTP client library can also be passed,
see documentation for specific :code:`Session` and :code:`AsyncSession` subclasses.
