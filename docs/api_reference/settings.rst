Settings
========

The following settings can be accessed and changed at runtime in `yadisk.settings` module:

* **DEFAULT_TIMEOUT** - `tuple` of 2 numbers (`int` or float`), default timeout for requests. First number is the connect timeout, the second one is the read timeout.
* **DEFAULT_N_RETRIES** - `int`, default number of retries
* **DEFAULT_RETRY_INTERVAL** - `float`, default retry interval
* **DEFAULT_UPLOAD_TIMEOUT** - analogous to `DEFAULT_TIMEOUT` but for `upload` function
* **DEFAULT_UPLOAD_RETRY_INTERVAL** - analogous to `DEFAULT_RETRY_INTERVAL` but for `upload` function
