Introduction
============

YaDisk is a Yandex.Disk REST API client library.

Installation
************

:code:`yadisk` supports multiple HTTP client libraries and has both synchronous and
asynchronous API.

The following HTTP client libraries are currently supported:

* :code:`requests` (used by default for synchronous API)
* :code:`httpx` (both synchronous and asynchronous, used by default for asynchronous API)
* :code:`aiohttp` (asynchronous only)
* :code:`pycurl` (synchronous only)

For synchronous API (installs :code:`requests`):

.. code:: bash

   pip install yadisk[sync_defaults]

For asynchronous API (installs :code:`aiofiles` and :code:`httpx`):

.. code:: bash

   pip install yadisk[async_defaults]

Alternatively, you can manually choose which optional libraries to install:

.. code:: bash

   # For use with pycurl
   pip install yadisk pycurl

   # For use with aiohttp, will also install aiofiles
   pip install yadisk[async_files] aiohttp

Examples
********

Synchronous API
---------------

.. code:: python

    import yadisk

    client = yadisk.Client(token="<token>")
    # or
    # client = yadisk.Client("<application-id>", "<application-secret>", "<token>")

    # You can either use the with statement or manually call client.close() later
    with client:
        # Check if the token is valid
        print(client.check_token())

        # Get disk information
        print(client.get_disk_info())

        # Print files and directories at "/some/path"
        print(list(client.listdir("/some/path")))

        # Upload "file_to_upload.txt" to "/destination.txt"
        client.upload("file_to_upload.txt", "/destination.txt")

        # Same thing
        with open("file_to_upload.txt", "rb") as f:
            client.upload(f, "/destination.txt")

        # Download "/some-file-to-download.txt" to "downloaded.txt"
        client.download("/some-file-to-download.txt", "downloaded.txt")

        # Permanently remove "/file-to-remove"
        client.remove("/file-to-remove", permanently=True)

        # Create a new directory at "/test-dir"
        print(client.mkdir("/test-dir"))

Receiving token with confirmation code
######################################

.. code:: python

    import sys
    import yadisk

    def main():
        with yadisk.Client("application-id>", "<application-secret>") as client:
            url = client.get_code_url()

            print(f"Go to the following url: {url}")
            code = input("Enter the confirmation code: ")

            try:
                response = client.get_token(code)
            except yadisk.exceptions.BadRequestError:
                print("Bad code")
                return

            client.token = response.access_token

            if client.check_token():
                print("Sucessfully received token!")
            else:
                print("Something went wrong. Not sure how though...")

    main()

Recursive upload
################

.. code:: python

    import posixpath
    import os
    import yadisk

    def recursive_upload(client: yadisk.Client, from_dir: str, to_dir: str):
        for root, dirs, files in os.walk(from_dir):
            p = root.split(from_dir)[1].strip(os.path.sep)
            dir_path = posixpath.join(to_dir, p)

            try:
                client.mkdir(dir_path)
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

    client = yadisk.Client(token="<application-token>")
    to_dir = "/test"
    from_dir = "/home/ubuntu"
    recursive_upload(client, from_dir, to_dir)

Setting custom properties of files
##################################

.. code:: python

    import yadisk

    def main():
        with yadisk.Client(token="<application-token>") as client:
            path = input("Enter a path to patch: ")
            properties = {"speed_of_light":       299792458,
                          "speed_of_light_units": "meters per second",
                          "message_for_owner":    "MWAHAHA! Your file has been patched by an evil script!"}

            meta = client.patch(path, properties)
            print("\nNew properties: ")

            for k, v in meta.custom_properties.items():
                print(f"{k}: {repr(v)}")

            answer = input("\nWant to get rid of them? (y/[n]) ")

            if answer.lower() in ("y", "yes"):
                properties = {k: None for k in properties}
                client.patch(path, properties)
                print("Everything's back as usual")

    main()

Emptying the trash bin
######################

.. code:: python

    import sys
    import yadisk

    def main():
        answer = input("Are you sure about this? (y/[n]) ")
        if answer.lower() not in ("y", "yes"):
            print("Not going to do anything")
            return

        with yadisk.Client(token="<application-token>") as client:
            print("Emptying the trash bin...")
            print("It might take a while...")

            client.remove_trash("/")

            print("Success!")

    main()

Specifying HTTP client library
##############################

.. code:: python

   import yadisk

   # Will use httpx for making requests
   with yadisk.Client(token="<token>", session="httpx") as client:
       print(client.check_token())

Asynchronous API
----------------

.. code:: python

    import yadisk
    import aiofiles

    client = yadisk.AsyncClient(token="<token>")
    # or
    # client = yadisk.AsyncClient("<application-id>", "<application-secret>", "<token>")

    # You can either use the with statement or manually call client.close() later
    async with client:
        # Check if the token is valid
        print(await client.check_token())

        # Get disk information
        print(await client.get_disk_info())

        # Print files and directories at "/some/path"
        print([i async for i in client.listdir("/some/path")])

        # Upload "file_to_upload.txt" to "/destination.txt"
        await client.upload("file_to_upload.txt", "/destination.txt")

        # Same thing
        async with aiofiles.open("file_to_upload.txt", "rb") as f:
            await client.upload(f, "/destination.txt")

        # Same thing but with regular files
        with open("file_to_upload.txt", "rb") as f:
            await client.upload(f, "/destination.txt")

        # Download "/some-file-to-download.txt" to "downloaded.txt"
        await client.download("/some-file-to-download.txt", "downloaded.txt")

        # Same thing
        async with aiofiles.open("downloaded.txt", "wb") as f:
            await client.download("/some-file-to-download.txt", f)

        # Permanently remove "/file-to-remove"
        await client.remove("/file-to-remove", permanently=True)

        # Create a new directory at "/test-dir"
        print(await client.mkdir("/test-dir"))

Receiving token with confirmation code
######################################

.. code:: python

    import asyncio
    import sys
    import yadisk

    async def main():
        async with yadisk.AsyncClient("application-id>", "<application-secret>") as client:
            url = client.get_code_url()

            print(f"Go to the following url: {url}")
            code = input("Enter the confirmation code: ")

            try:
                response = await client.get_token(code)
            except yadisk.exceptions.BadRequestError:
                print("Bad code")
                return

            client.token = response.access_token

            if await client.check_token():
                print("Sucessfully received token!")
            else:
                print("Something went wrong. Not sure how though...")

    asyncio.run(main())

Recursive upload
################

.. code:: python

    import asyncio
    import posixpath
    import os
    import yadisk

    async def recursive_upload(from_dir: str, to_dir: str, n_parallel_requests: int = 5):
        async with yadisk.AsyncClient(token="<application-token>") as client:
            async def upload_files(queue):
                while queue:
                    in_path, out_path = queue.pop(0)

                    print(f"Uploading {in_path} -> {out_path}")

                    try:
                        await client.upload(in_path, out_path)
                    except yadisk.exceptions.PathExistsError:
                        print(f"{out_path} already exists")

            async def create_dirs(queue):
                while queue:
                    path = queue.pop(0)

                    print(f"Creating directory {path}")

                    try:
                        await client.mkdir(path)
                    except yadisk.exceptions.PathExistsError:
                        print(f"{path} already exists")

            mkdir_queue = []
            upload_queue = []

            print(f"Creating directory {to_dir}")

            try:
                await client.mkdir(to_dir)
            except yadisk.exceptions.PathExistsError:
                print(f"{to_dir} already exists")

            for root, dirs, files in os.walk(from_dir):
                rel_dir_path = root.split(from_dir)[1].strip(os.path.sep)
                rel_dir_path = rel_dir_path.replace(os.path.sep, "/")
                dir_path = posixpath.join(to_dir, rel_dir_path)

                for dirname in dirs:
                    mkdir_queue.append(posixpath.join(dir_path, dirname))

                for filename in files:
                    out_path = posixpath.join(dir_path, filename)
                    rel_dir_path_sys = rel_dir_path.replace("/", os.path.sep)
                    in_path = os.path.join(from_dir, rel_dir_path_sys, filename)

                    upload_queue.append((in_path, out_path))

                tasks = [upload_files(upload_queue) for i in range(n_parallel_requests)]
                tasks.extend(create_dirs(mkdir_queue) for i in range(n_parallel_requests))

                await asyncio.gather(*tasks)

    from_dir = input("Directory to upload: ")
    to_dir = input("Destination directory: ")

    asyncio.run(recursive_upload(from_dir, to_dir, 5))

Setting custom properties of files
##################################

.. code:: python

    import asyncio
    import yadisk

    async def main():
        async with yadisk.AsyncClient(token="<application-token>") as client:
            path = input("Enter a path to patch: ")
            properties = {"speed_of_light":       299792458,
                          "speed_of_light_units": "meters per second",
                          "message_for_owner":    "MWAHAHA! Your file has been patched by an evil script!"}

            meta = await client.patch(path, properties)
            print("\nNew properties: ")

            for k, v in meta.custom_properties.items():
                print(f"{k}: {repr(v)}")

            answer = input("\nWant to get rid of them? (y/[n]) ")

            if answer.lower() in ("y", "yes"):
                properties = {k: None for k in properties}
                await client.patch(path, properties)
                print("Everything's back as usual")

    asyncio.run(main())

Emptying the trash bin
######################

.. code:: python

    import asyncio
    import sys
    import yadisk

    async def main():
        answer = input("Are you sure about this? (y/[n]) ")

        if answer not in ("y", "yes"):
            print("Not going to do anything")
            return

        async with yadisk.AsyncClient(token="<application-token>") as client:
            print("Emptying the trash bin...")
            print("It might take a while...")

            await client.remove_trash("/")
            print("Success!")

    asyncio.run(main())

Specifying HTTP client library
##############################

.. code:: python

   import yadisk

   # Will use aiohttp for making requests
   async with yadisk.AsyncClient(token="<token>", session="aiohttp") as client:
       print(await client.check_token())
