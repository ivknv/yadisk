YaDisk
======

YaDisk is a Yandex.Disk REST API client library.

.. _Read the Docs (EN): http://yadisk.readthedocs.io
.. _Read the Docs (RU): http://yadisk.readthedocs.io/ru/latest

Documentation is available at `Read the Docs (EN)`_ and `Read the Docs (RU)`_ (although it's not complete yet).

Installation
************

First, you need to have `requests` installed.

.. code:: bash

    pip install yadisk requests

or

.. code:: bash

    python setup.py install

Examples
********

.. code:: python

    import yadisk

    y = yadisk.YaDisk("<application-id>", "<application-secret>", "<token>")

    # Check if the token is valid
    print(y.check_token())

    # Get disk information
    print(y.get_disk_info())

    # Print files and directories at "/some/path"
    print(list(y.listdir("/some/path")))

    # Upload "file_to_upload.txt" to "/destination.txt"
    y.upload("file_to_upload.txt", "/destination.txt")

    # Same thing
    with open("file_to_upload.txt", "rb") as f:
        y.upload(f, "/destination.txt")

    # Download "/some-file-to-download.txt" to "downloaded.txt"
    y.download("/some-file-to-download.txt", "downloaded.txt")

    # Permanently remove "/file-to-remove"
    y.remove("/file-to-remove", permanently=True)

    # Create a new directory at "/test-dir"
    print(y.mkdir("/test-dir"))
