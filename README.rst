YaDisk
======

YaDisk &#8212; это библиотека-клиент REST API Яндекс.Диска.

.. _Read the Docs (EN): http://yadisk.readthedocs.io
.. _Read the Docs (RU): http://yadisk.readthedocs.io/ru/latest

Документация доступна на `Read the Docs (RU)`_ и `Read the Docs (EN)`_.

Установка
*********

Для начала, должен быть установлен `requests`:

.. code:: bash

    pip install requests

.. code:: bash

    python setup.py install

Примеры
*******

.. code:: python

    import yadisk

    y = yadisk.YaDisk("<id-приложения>", "<secret-приложения>", "<токен>")

    # Проверяет, валиден ли токен
    print(y.check_token())

    # Получает общую информацию о диске
    print(y.get_disk_info())

    # Выводит содержимое "/some/path"
    print(list(y.listdir("/some/path")))

    # Загружает "file_to_upload.txt" в "/destination.txt"
    y.upload("file_to_upload.txt", "/destination.txt")

    # То же самое
    with open("file_to_upload.txt", "rb") as f:
        y.upload(f, "/destination.txt")

    # Скачивает "/some-file-to-download.txt" в "downloaded.txt"
    y.download("/some-file-to-download.txt", "downloaded.txt")

    # Безвозвратно удаляет "/file-to-remove"
    y.remove("/file-to-remove", permanently=True)

    # Создаёт новую папку "/test-dir"
    print(y.mkdir("/test-dir"))
