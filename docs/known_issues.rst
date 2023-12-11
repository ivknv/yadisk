Known Issues
============

Very Slow Upload of Certain Types of Files
##########################################

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

Low Upload Speed on Windows When Using requests
###############################################

.. _requests: https://pypi.org/project/requests
.. _httpx: https://pypi.org/project/httpx

If you use `requests`_ and experience low upload speeds on Windows, the reason
might be due to Python's standard library internally using :code:`select()` to
wait for sockets. The best way around it is to use a different HTTP library
(e.g. `httpx`_, see :doc:`/api_reference/sessions`)
