Known Issues
============

Very Slow Upload of Certain Types of Files
##########################################

.. note::

   The following information may become outdated at some point in the future.

Yandex.Disk's REST API limits upload speeds up to 128 KiB/s for certain MIME types of files.
More specifically, throttling takes place based on value of :code:`media_type`
(see :any:`yadisk.Client.get_meta`).
It appears there are 3 types of media types that are throttled:

1) :code:`data` (.db, .dat, etc.)
2) :code:`compressed` (.zip, .gz, .tgz, .rar, .etc)
3) :code:`video` (.3gp, .mp4, .avi, etc.)

This behavior of throttling is predetermined at the moment of requesting an
upload link (with :any:`yadisk.Client.get_upload_link`). The content of the
uploaded file does not matter.

The reason why this problem cannot be observed when uploading through the
official website, is that this throttling does not apply to internal services
(the Yandex.Disk website uses an intermediate internal API to obtain upload links).

While it is not clear what the purpose of this throttling is, it is certain at
this point that this is not a bug.

The only known workaround is to upload files with changed filename extensions (or without them entirely).
For example, if you want to upload a file named "my_database.db", you can initially
upload it under the name "my_database.some_other_extension" and then rename it back
to "my_database.db". This approach has some obvious downsides but at least it
works.

Low Upload Speed on Windows
###########################

.. _http.client: https://docs.python.org/3/library/http.client.html
.. _urllib3: https://pypi.org/project/urllib3/
.. _eventlet: https://pypi.org/project/eventlet
.. _yadisk-async: https://pypi.org/project/yadisk-async
.. _aiohttp: https://pypi.org/project/aiohttp
.. _requests: https://pypi.org/project/requests

If you experience low upload speeds on Windows, the reason might be due to
Python's standard library internally using :code:`select()` to wait for sockets.
There are several ways around it:

1) Monkey-patching `http.client`_ and `urllib3`_ to use bigger :code:`blocksize`.
   See `this comment <https://github.com/urllib3/urllib3/issues/1394#issuecomment-954044006>`_ for more details.
2) Monkey-patching through a library like `eventlet`_.
3) Using `yadisk-async`_ instead. It uses `aiohttp`_ instead of `requests`_.
4) Uploading files to direct links (obtained through :any:`yadisk.Client.get_upload_link()`) using
   a different library (such as `aiohttp`_).
