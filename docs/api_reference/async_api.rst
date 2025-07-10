Asynchronous API
================

.. autoclass:: yadisk.AsyncClient

   .. automethod:: close

.. autoclass:: yadisk.AsyncYaDisk

Authentication
--------------

.. automethod:: yadisk.AsyncClient.check_token
.. automethod:: yadisk.AsyncClient.get_auth_url
.. automethod:: yadisk.AsyncClient.get_code_url
.. automethod:: yadisk.AsyncClient.get_device_code
.. automethod:: yadisk.AsyncClient.get_token
.. automethod:: yadisk.AsyncClient.get_token_from_device_code
.. automethod:: yadisk.AsyncClient.refresh_token
.. automethod:: yadisk.AsyncClient.revoke_token

Disk Info
---------

.. automethod:: yadisk.AsyncClient.get_disk_info

Metadata About Files
--------------------

.. automethod:: yadisk.AsyncClient.get_meta
.. automethod:: yadisk.AsyncClient.listdir
.. automethod:: yadisk.AsyncClient.exists
.. automethod:: yadisk.AsyncClient.get_type
.. automethod:: yadisk.AsyncClient.is_file
.. automethod:: yadisk.AsyncClient.is_dir
.. automethod:: yadisk.AsyncClient.get_files
.. automethod:: yadisk.AsyncClient.get_last_uploaded

Uploading Files
---------------

.. automethod:: yadisk.AsyncClient.upload
.. automethod:: yadisk.AsyncClient.get_upload_link
.. automethod:: yadisk.AsyncClient.get_upload_link_object
.. automethod:: yadisk.AsyncClient.upload_by_link
.. automethod:: yadisk.AsyncClient.upload_url

Downloading Files
-----------------

.. automethod:: yadisk.AsyncClient.download
.. automethod:: yadisk.AsyncClient.get_download_link
.. automethod:: yadisk.AsyncClient.download_by_link


File Operations
---------------

Creating Directories
^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.AsyncClient.mkdir
.. automethod:: yadisk.AsyncClient.makedirs


Removing Files
^^^^^^^^^^^^^^
.. automethod:: yadisk.AsyncClient.remove

Copying Files
^^^^^^^^^^^^^
.. automethod:: yadisk.AsyncClient.copy

Moving Files
^^^^^^^^^^^^

.. automethod:: yadisk.AsyncClient.move
.. automethod:: yadisk.AsyncClient.rename

Setting Custom Properties
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.AsyncClient.patch

Public Files
------------

Publishing/Unpublishing Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.AsyncClient.publish
.. automethod:: yadisk.AsyncClient.unpublish

Metadata About Public Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.AsyncClient.get_public_meta
.. automethod:: yadisk.AsyncClient.get_public_type
.. automethod:: yadisk.AsyncClient.is_public_dir
.. automethod:: yadisk.AsyncClient.is_public_file
.. automethod:: yadisk.AsyncClient.public_exists

Downloading Public Files
^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.AsyncClient.get_public_download_link
.. automethod:: yadisk.AsyncClient.download_public

Saving Public Resources to Disk
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.AsyncClient.save_to_disk

Listing Public Files
^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.AsyncClient.get_public_resources
.. automethod:: yadisk.AsyncClient.get_all_public_resources

Public Access Settings
----------------------

.. automethod:: yadisk.AsyncClient.get_public_settings
.. automethod:: yadisk.AsyncClient.get_public_available_settings
.. automethod:: yadisk.AsyncClient.update_public_settings

Trash
-----

.. automethod:: yadisk.AsyncClient.get_trash_meta
.. automethod:: yadisk.AsyncClient.trash_exists
.. automethod:: yadisk.AsyncClient.restore_trash
.. automethod:: yadisk.AsyncClient.remove_trash
.. automethod:: yadisk.AsyncClient.trash_listdir
.. automethod:: yadisk.AsyncClient.get_trash_type
.. automethod:: yadisk.AsyncClient.is_trash_dir
.. automethod:: yadisk.AsyncClient.is_trash_file

Checking Operation Status
-------------------------

.. automethod:: yadisk.AsyncClient.get_operation_status
.. automethod:: yadisk.AsyncClient.wait_for_operation
