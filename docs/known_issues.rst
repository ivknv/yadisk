Known Issues
============

Very Slow Upload of Certain Types of Files
##########################################

For whatever reason, files with specific extensions take much longer time to upload.
Here are some known extensions with this problem:

1. :code:`.db`
2. :code:`.mp4`
3. :code:`.avi`
4. :code:`.3gp`
5. :code:`.rar`
6. :code:`.zip`
7. :code:`.gz`
8. :code:`.tgz`
9. :code:`.dat`
10. ...and more.

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
4) Uploading files to direct links (obtained through :any:`yadisk.YaDisk.get_upload_link()`) using
   a different library (such as `aiohttp`_).

Upload Timeout on Large Files
#############################

When uploading large files (over a couple of GB in size) you may experience
timeout errors after the full upload. This might be caused by Yandex.Disk computing
hash sums or doing some other operations. The bigger the file, the bigger the
timeouts may need to be set.
