Synchronous API
===============

.. autoclass:: yadisk.Client

   .. automethod:: close

.. autoclass:: yadisk.YaDisk

Authentication
--------------

.. automethod:: yadisk.Client.check_token
.. automethod:: yadisk.Client.get_auth_url
.. automethod:: yadisk.Client.get_code_url
.. automethod:: yadisk.Client.get_device_code
.. automethod:: yadisk.Client.get_token
.. automethod:: yadisk.Client.get_token_from_device_code
.. automethod:: yadisk.Client.refresh_token
.. automethod:: yadisk.Client.revoke_token

Disk Info
---------

.. automethod:: yadisk.Client.get_disk_info

Metadata About Files
--------------------

.. automethod:: yadisk.Client.get_meta
.. automethod:: yadisk.Client.listdir
.. automethod:: yadisk.Client.exists
.. automethod:: yadisk.Client.get_type
.. automethod:: yadisk.Client.is_file
.. automethod:: yadisk.Client.is_dir
.. automethod:: yadisk.Client.get_files
.. automethod:: yadisk.Client.get_last_uploaded

Uploading Files
---------------

.. automethod:: yadisk.Client.upload
.. automethod:: yadisk.Client.get_upload_link
.. automethod:: yadisk.Client.get_upload_link_object
.. automethod:: yadisk.Client.upload_by_link
.. automethod:: yadisk.Client.upload_url

Downloading Files
-----------------

.. automethod:: yadisk.Client.download
.. automethod:: yadisk.Client.get_download_link
.. automethod:: yadisk.Client.download_by_link


File Operations
---------------

Creating Directories
^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.Client.mkdir
.. automethod:: yadisk.Client.makedirs


Removing Files
^^^^^^^^^^^^^^
.. automethod:: yadisk.Client.remove

Copying Files
^^^^^^^^^^^^^
.. automethod:: yadisk.Client.copy

Moving Files
^^^^^^^^^^^^

.. automethod:: yadisk.Client.move
.. automethod:: yadisk.Client.rename

Setting Custom Properties
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.Client.patch

Public Files
------------

Publishing/Unpublishing Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.Client.publish
.. automethod:: yadisk.Client.unpublish


Metadata About Public Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.Client.get_public_meta
.. automethod:: yadisk.Client.get_public_type
.. automethod:: yadisk.Client.is_public_dir
.. automethod:: yadisk.Client.is_public_file
.. automethod:: yadisk.Client.public_exists

Downloading Public Files
^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.Client.get_public_download_link
.. automethod:: yadisk.Client.download_public

Saving Public Resources to Disk
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.Client.save_to_disk

Listing Public Files
^^^^^^^^^^^^^^^^^^^^

.. automethod:: yadisk.Client.get_public_resources
.. automethod:: yadisk.Client.get_all_public_resources

Public Access Settings
----------------------

.. automethod:: yadisk.Client.get_public_settings
.. automethod:: yadisk.Client.get_public_available_settings
.. automethod:: yadisk.Client.update_public_settings

Trash
-----

.. automethod:: yadisk.Client.get_trash_meta
.. automethod:: yadisk.Client.trash_exists
.. automethod:: yadisk.Client.restore_trash
.. automethod:: yadisk.Client.remove_trash
.. automethod:: yadisk.Client.trash_listdir
.. automethod:: yadisk.Client.get_trash_type
.. automethod:: yadisk.Client.is_trash_dir
.. automethod:: yadisk.Client.is_trash_file

Checking Operation Status
-------------------------

.. automethod:: yadisk.Client.get_operation_status
.. automethod:: yadisk.Client.wait_for_operation
