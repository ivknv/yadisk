Introduction
============

YaDisk is a Yandex.Disk REST API client library.

Installation
************

.. code:: bash

    pip install yadisk

or

.. code:: bash

    python setup.py install

Examples
********

.. code:: python

    import yadisk

    y = yadisk.YaDisk(token="<token>")
    # or
    # y = yadisk.YaDisk("<application-id>", "<application-secret>", "<token>")

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

Receiving token with confirmation code
######################################

.. code:: python

    import sys
    import yadisk

    y = yadisk.YaDisk("application-id>", "<application-secret>")
    url = y.get_code_url()

    print("Go to the following url: %s" % url)
    code = input("Enter the confirmation code: ")

    try:
        response = y.get_token(code)
    except yadisk.exceptions.BadRequestError:
        print("Bad code")
        sys.exit(1)

    y.token = response.access_token

    if y.check_token():
        print("Sucessfully received token!")
    else:
        print("Something went wrong. Not sure how though...")


Recursive upload
################

.. code:: python

    import posixpath
    import os
    import yadisk

    def recursive_upload(y, from_dir, to_dir):
        for root, dirs, files in os.walk(from_dir):
         p = root.split(from_dir)[1].strip(os.path.sep)
         dir_path = posixpath.join(to_dir, p)

         try:
            y.mkdir(dir_path)
         except yadisk.exceptions.PathExistsError:
            pass

         for file in files:
             file_path = posixpath.join(dir_path, file)
             p_sys = p.replace("/", os.path.sep)
             in_path = os.path.join(from_dir, p_sys, file)
             try:
                 y.upload(in_path, file_path)
             except yadisk.exceptions.PathExistsError:
                 pass

    y = yadisk.YaDisk(token="<application-token>")
    to_dir = "/test"
    from_dir = "/home/ubuntu"
    recursive_upload(y, from_dir, to_dir)

Setting custom properties of files
##################################

.. code:: python

    import yadisk

    y = yadisk.YaDisk(token="<application-token>")

    path = input("Enter a path to patch: ")
    properties = {"speed_of_light":       299792458,
                  "speed_of_light_units": "meters per second",
                  "message_for_owner":    "MWAHAHA! Your file has been patched by an evil script!"}

    meta = y.patch(path, properties)
    print("\nNew properties: ")

    for k, v in meta.custom_properties.items():
        print("%s: %r" % (k, v))

    answer = input("\nWant to get rid of them? (y/[n]) ")

    if answer.lower() in ("y", "yes"):
        properties = {k: None for k in properties}
        y.patch(path, properties)
        print("Everything's back as usual")

Emptying the trash bin
######################

.. code:: python

    import sys
    import time
    import yadisk

    y = yadisk.YaDisk(token="<application-token>")

    answer = input("Are you sure about this? (y/[n]) ")

    if answer.lower() in ("y", "yes"):
        print("Emptying the trash bin...")
        operation = y.remove_trash("/")
        print("It might take a while...")

        if operation is None:
            print("Nevermind. The deed is done.")
            sys.exit(0)

        while True:
            status = y.get_operation_status(operation.href)

            if status == "in-progress":
                time.sleep(5)
                print("Still waiting...")
            elif status == "success":
                print("Success!")
                break
            else:
                print("Got some weird status: %r" % (status,))
                print("That's not normal")
                break
    else:
        print("Not going to do anything")
