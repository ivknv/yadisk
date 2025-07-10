YaDisk
======

.. |RTD Badge| image:: https://img.shields.io/readthedocs/yadisk.svg
   :alt: Read the Docs
   :target: https://yadisk.readthedocs.io/ru/latest/

.. |CI Badge| image:: https://img.shields.io/github/actions/workflow/status/ivknv/yadisk/lint_and_test.yml
   :alt: GitHub Actions Workflow Status

.. |PyPI Badge| image:: https://img.shields.io/pypi/v/yadisk.svg
   :alt: PyPI
   :target: https://pypi.org/project/yadisk

.. |Python Version Badge| image:: https://img.shields.io/pypi/pyversions/yadisk
   :alt: PyPI - Python Version

.. |Coverage Badge| image:: https://coveralls.io/repos/github/ivknv/yadisk/badge.svg?branch=master
   :alt: Coverage
   :target: https://coveralls.io/github/ivknv/yadisk

|RTD Badge| |CI Badge| |PyPI Badge| |Python Version Badge| |Coverage Badge|

.. _English version of this document: https://github.com/ivknv/yadisk/blob/master/README.en.rst

`English version of this document`_

YaDisk - это библиотека-клиент REST API Яндекс.Диска.

.. _Read the Docs (EN): https://yadisk.readthedocs.io
.. _Read the Docs (RU): https://yadisk.readthedocs.io/ru/latest

Документация доступна на `Read the Docs (RU)`_ и `Read the Docs (EN)`_.

.. contents:: Содержание:

Установка
*********

:code:`yadisk` поддерживает несколько HTTP библиотек и реализует одновременно как синхронный,
так и асинхронный API.

На данный момент поддерживаются следующие HTTP библиотеки:

* :code:`requests` (используется по умолчанию для синхронного API)
* :code:`httpx` (синхронный и асинхронный API, используется по умолчанию для асинхронного API)
* :code:`aiohttp` (асинхронный API)
* :code:`pycurl` (синхронный API)

Для синхронного API (устанавливает :code:`requests`):

.. code:: bash

    pip install yadisk[sync-defaults]

Для асинхронного API (устанавливает :code:`httpx` и :code:`aiofiles`):

.. code:: bash

   pip install yadisk[async-defaults]

Вы можете также вручную установить нужные библиотеки:

.. code:: bash

   # Для использования совместно с pycurl
   pip install yadisk[pycurl]

   # Для использования совместно с aiohttp, также установит aiofiles
   pip install yadisk[async-files,aiohttp]

Примеры
*******

Синхронный API
--------------

.. code:: python

    import yadisk

    client = yadisk.Client(token="<токен>")
    # или
    # client = yadisk.Client("<id-приложения>", "<secret-приложения>", "<токен>")

    # Вы можете использовать либо конструкцию with, либо вручную вызвать client.close() в конце
    with client:
        # Проверяет, валиден ли токен
        print(client.check_token())

        # Получает общую информацию о диске
        print(client.get_disk_info())

        # Выводит содержимое "/some/path"
        print(list(client.listdir("/some/path")))

        # Загружает "file_to_upload.txt" в "/destination.txt"
        client.upload("file_to_upload.txt", "/destination.txt")

        # То же самое
        with open("file_to_upload.txt", "rb") as f:
            client.upload(f, "/destination.txt")

        # Скачивает "/some-file-to-download.txt" в "downloaded.txt"
        client.download("/some-file-to-download.txt", "downloaded.txt")

        # Безвозвратно удаляет "/file-to-remove"
        client.remove("/file-to-remove", permanently=True)

        # Создаёт новую папку "/test-dir"
        print(client.mkdir("/test-dir"))

Асинхронный API
---------------

.. code:: python

    import yadisk
    import aiofiles

    client = yadisk.AsyncClient(token="<token>")
    # или
    # client = yadisk.AsyncClient("<application-id>", "<application-secret>", "<token>")

    # Вы можете использовать либо конструкцию with, либо вручную вызвать client.close() в конце
    async with client:
        # Проверяет, валиден ли токен
        print(await client.check_token())

        # Получает общую информацию о диске
        print(await client.get_disk_info())

        # Выводит содержимое "/some/path"
        print([i async for i in client.listdir("/some/path")])

        # Загружает "file_to_upload.txt" в "/destination.txt"
        await client.upload("file_to_upload.txt", "/destination.txt")

        # То же самое
        async with aiofiles.open("file_to_upload.txt", "rb") as f:
            await client.upload(f, "/destination.txt")

        # То же самое, но с обычными файлами
        with open("file_to_upload.txt", "rb") as f:
            await client.upload(f, "/destination.txt")

        # Скачивает "/some-file-to-download.txt" в "downloaded.txt"
        await client.download("/some-file-to-download.txt", "downloaded.txt")

        # То же самое
        async with aiofiles.open("downloaded.txt", "wb") as f:
            await client.download("/some-file-to-download.txt", f)

        # Безвозвратно удаляет "/file-to-remove"
        await client.remove("/file-to-remove", permanently=True)

        # Создаёт новую папку "/test-dir"
        print(await client.mkdir("/test-dir"))

Участие в разработке
********************

Если вы хотите поучаствовать в разработке, см.
`CONTRIBUTING.rst <https://github.com/ivknv/yadisk/blob/master/CONTRIBUTING.rst>`_.

История изменений
*****************

.. _issue #2: https://github.com/ivknv/yadisk/issues/2
.. _issue #4: https://github.com/ivknv/yadisk/issues/4
.. _issue #7: https://github.com/ivknv/yadisk/issues/7
.. _issue #23: https://github.com/ivknv/yadisk/issues/23
.. _issue #26: https://github.com/ivknv/yadisk/issues/26
.. _issue #28: https://github.com/ivknv/yadisk/issues/28
.. _issue #29: https://github.com/ivknv/yadisk/issues/29
.. _PR #31: https://github.com/ivknv/yadisk/pull/31
.. _issue #43: https://github.com/ivknv/yadisk/issues/43
.. _issue #45: https://github.com/ivknv/yadisk/issues/45
.. _issue #49: https://github.com/ivknv/yadisk/issues/49
.. _issue #53: https://github.com/ivknv/yadisk/issues/53
.. _Введение: https://yadisk.readthedocs.io/ru/latest/intro.html
.. _Справочник API: https://yadisk.readthedocs.io/ru/latest/api_reference/index.html
.. _Доступные реализации сессий: https://yadisk.readthedocs.io/ru/latest/api_reference/sessions.html
.. _Интерфейс Session: https://yadisk.readthedocs.io/ru/latest/api_reference/session_interface.html
.. _requests: https://pypi.org/project/requests
.. _Руководство по миграции: https://yadisk.readthedocs.io/ru/latest/migration_guide.html
.. _PR #57: https://github.com/ivknv/yadisk/pull/57

* **Release 3.4.0 (2025-07-10)**

  * Нововведения:

    * Добавлены методы для управления настройками публичного доступа к ресурсам:

      * :code:`Client.update_public_settings()`
      * :code:`Client.get_public_settings()`
      * :code:`Client.get_public_available_settings()`

      Внимание: похоже, что эти эндпоинты не полностью соответствуют
      официальной документации REST API, их функциональность на практике
      ограничена.

    * Добавлен новый класс исключений :code:`PasswordRequiredError`

    * Добавлено несколько новых полей :code:`DiskInfoObject`:

      * :code:`deletion_restricion_days`
      * :code:`hide_screenshots_in_photoslice`
      * :code:`is_legal_entity`

    * Реализован метод :code:`__dir__()` для объектов ответов сервера

  * Улучшения:

    * :code:`repr()` объектов ответов API теперь показывает только те ключи,
      которые фактически присутствуют (вместо отображения их значений как
      :code:`None`, как раньше)

* **Release 3.3.0 (2025-04-29)**

  * Нововведения:

    * Спуфинг User-Agent для обхода ограничения скорости загрузки файлов на
      Диск (см. `PR #57`_). :code:`Client.upload()` и связанные с ним методы
      (включая :code:`AsyncClient`) имеют новый опциональный параметр
      :code:`spoof_user_agent`, который по умолчанию имеет значение
      :code:`True`. Этот параметр можно использовать для отключения спуфинга,
      если это необходимо.

    * Добавлена поддержка pretty-printing в IPython для :code:`YaDiskObject` и
      производных классов

  * Исправления:

    * :code:`Client.wait_for_operation()` теперь использует
      :code:`time.monotonic()` вместо :code:`time.time()`

  * Улучшения:

    * Сообщения об ошибках REST API теперь чётко разделены на четыре части
      (сообщение, описание, код ошибки и код состояния HTTP)

* **Release 3.2.0 (2025-02-03)**

  * Нововведения:

    * Добавлен новый метод: :code:`Client.makedirs()` и
      :code:`AsyncClient.makedirs()` (см. `issue #53`_)
    * Добавлено несколько недостающих полей :code:`DiskInfoObject`

      * :code:`photounlim_size`
      * :code:`will_be_overdrawn`
      * :code:`free_photounlim_end_date`
      * :code:`payment_flow`

    * Добавлено недостающее поле :code:`sizes` для :code:`ResourceObject` и
      связанных с ним объектов

  * Исправления:

    * :code:`Client.rename()` / :code:`AsyncClient.rename()` теперь вызывает
      :code:`ValueError` при попытке переименовать корневую папку
    * Номера автоматических повторных попыток логировались с ошибкой на
      единицу, теперь они логируются правильно

* **Release 3.1.0 (2024-07-12)**

  * Нововведения:

    * Добавлены новые исключения: :code:`GoneError` и
      :code:`ResourceDownloadLimitExceededError`
    * Добавлен новый метод: :code:`Client.get_all_public_resources()` и
      :code:`AsyncClient.get_all_public_resources()`
  * Исправления:

    * Задание :code:`headers` и других опциональных параметров сессии как
      :code:`None` больше не вызывает ошибок
    * Исправлено неправильное поведение :code:`Client.rename()` и
      :code:`AsyncClient.rename()` при указании пустого имени файла
    * Исправлено несколько опечаток в асинхронных реализациях
      convenience-методов (:code:`listdir()` и аналогичных)
    * Исправлен неправильный тип данных у атрибута :code:`items` класса
      :code:`PublicResourceListObject`
    * Исправлены ошибки при отправке запросов API с помощью
      :code:`PycURLSession` при задании :code:`stream=True`
    * Данные не будут записаны в файл методами :code:`Client.download()`,
      :code:`Client.download_by_link()`, :code:`AsyncClient.download()` и
      :code:`AsyncClient.download_by_link()`, если сервер вернул ошибочный код
      состояния

* **Release 3.0.1 (2024-07-09)**

  * Исправлен сломанный :code:`pyproject.toml`, который не включал в сборку
    полное содержимое пакета (см. `issue #49`_)

* **Release 3.0.0 (2024-07-09)**

  * Несовместимые изменения:

    - См. `Руководство по миграции`_ для подробностей
    - Все методы теперь ожидают завершения асинхронных операций по умолчанию
      (см. новый параметр :code:`wait=<bool>`)
    - Итерация по результату :code:`AsyncClient.listdir()` больше не требует
      дополнительного ключевого слова await
    - Число возвращаемых файлов :code:`Client.get_files()` /
      :code:`AsyncClient.get_files()` теперь контролируется параметром
      :code:`max_items`, вместо :code:`limit`
    - Методы :code:`set_token()`, :code:`set_headers()` интерфейсов
      :code:`Session` и :code:`AsyncSession` были удалены
    - Некоторые методы больше не принимают параметр :code:`fields`
    - :code:`Client.get_last_uploaded()` /
      :code:`AsyncClient.get_last_uploaded()` теперь возвращает список вместо
      генератора
    - :code:`yadisk.api` - теперь скрытый модуль
    - Все скрытые модули были переименованы, их имена начинаются с :code:`_`
      (например, :code:`yadisk._api`)
  * Нововведения:

    - Добавлены методы для ожидания завершения асинхронной операции (см.
      :code:`Client.wait_for_operation()` /
      :code:`AsyncClient.wait_for_operation()`)
    - Методы, которые могут запускать асинхронную операцию, теперь принимают
      дополнительные параметры: :code:`wait: bool = True`,
      :code:`poll_interval: float = 1.0` и
      :code:`poll_timeout: Optional[float] = None`
    - :code:`Client.listdir()`, :code:`Client.get_files()` и их асинхронные
      вариации теперь принимают новый параметр :code:`max_items: Optional[int] =
      None`, который может быть использован, чтобы ограничить максимальное число
      возвращаемых файлов
    - Большинство методов :code:`Client` и :code:`AsyncClient` теперь принимает
      :code:`retry_on: Optional[Tuple[Type[Exception], ...]] = None`, который
      позволяет указывать кортеж из дополнительных исключений, которые могут вызвать
      автоматическую повторную попытку
    - Модуль :code:`yadisk.types` - теперь публичный
    - Добавлено логирование исходящих запросов к API и автоматических
      повторных попыток
    - Объект логгера библиотеки доступен как :code:`yadisk.settings.logger`
    - Добавлен метод :code:`YaDiskObject.field()` и оператор :code:`@`
      (:code:`YaDiskObject.__matmul__()`), который удостоверяется, что указанное
      поле объекта не является :code:`None`
    - Добавлены методы :code:`Client.get_upload_link_object()`,
      :code:`AsyncClient.get_upload_link_object()`, возвращаемые значения которых
      дополнительно содержат :code:`operation_id`
    - :code:`utils.auto_retry()` теперь принимает больше параметров
    - Добавлено несколько недостающих полей :code:`DiskInfoObject`
    - :code:`EXIFObject` теперь содержит GPS-координаты
    - :code:`CaseInsensitiveDict` - теперь часть :code:`yadisk.utils`
  * Улучшения:

    - Добавлены полные подсказки типов для :code:`Client` и :code:`AsyncClient` с
      помощью файлов :code:`.pyi`
    - Строки документации для :code:`Client` / :code:`AsyncClient` теперь
      включают в себя больше параметров
    - Ошибки во время обработки JSON (например, :code:`InvalidResponseError`)
      также вызывают автоматические повторные попытки
    - Сообщение об ошибке в случае, когда модуль сессии по умолчанию
      недоступен, теперь не вводит в заблуждение (см. `issue #43`_)
    - Уменьшено значение :code:`limit` до :code:`500` (было :code:`10000`)
      для :code:`Client.listdir()` для избежания таймаутов при больших папках
      (см. `issue #45`_)
    - Уменьшено значение :code:`limit` до :code:`200` (было :code:`1000`)
      для :code:`Client.get_files()` для избежания таймаутов
    - :code:`Client.download()` и подобные методы больше не задают заголовок
      :code:`Connection: close` т.к. в этом нет необходимости (в отличие от
      :code:`Client.upload()`)
    - :code:`UnknownYaDiskError` теперь включает код статуса в сообщение об
      ошибке
  * Исправления:

    - Исправлены реализации на основе :code:`httpx` и :code:`aiohttp`:
      реализации методов :code:`Response.json()` / :code:`AsyncResponse.json()`
      не преобразовывали свои исключения в :code:`RequestError`
    - Исправлено: параметр :code:`stream=True` был не задан по умолчанию в
      :code:`AsyncClient.download()`, :code:`AsyncClient.download_public()`
  * Другие изменения:

    - :code:`typing_extensions` теперь требуется для Python < 3.10

* **Release 2.1.0 (2024-01-03)**

  * Исправлен баг, из-за которого параметры в теле POST-запроса неправильно кодировались
  * Исправлен баг в :code:`PycURLSession.send_request()`, из-за которого
    переданные заголовки игнорировались
  * :code:`RequestsSession.close()` теперь закрывает сессию для всех потоков
  * Все методы :code:`Client` и :code:`AsyncClient` теперь используют
    существующую сессию
  * Удалены аттрибут :code:`session_factory` и метод :code:`make_session()`
    классов :code:`Client` и :code:`AsyncClient`
  * Класс сессии теперь может быть указан в качестве строки
    (см. :code:`Client`/:code:`AsyncClient`)
  * Добавлены методы :code:`Client.get_device_code()`/:code:`AsyncClient.get_device_code()`
  * Добавлены методы :code:`Client.get_token_from_device_code()`/:code:`AsyncClient.get_token_from_device_code()`
  * Добавлен недостающий параметр :code:`redirect_uri` для
    :code:`Client.get_auth_url()`/:code:`AsyncClient.get_auth_url()` и
    :code:`Client.get_code_url()`/:code:`AsyncClient.get_code_url()`
  * Добавлена поддержка параметров PKCE для
    :code:`Client.get_auth_url()`/:code:`AsyncClient.get_auth_url()`,
    :code:`Client.get_code_url()`/:code:`AsyncClient.get_code_url()` и
    :code:`Client.get_token()`/:code:`AsyncClient.get_token()`
  * Добавлен аттрибут :code:`scope` для :code:`TokenObject`
  * Добавлены новые классы исключений: :code:`InvalidClientError`,
    :code:`InvalidGrantError`, :code:`AuthorizationPendingError`,
    :code:`BadVerificationCodeError` и :code:`UnsupportedTokenTypeError`

* **Release 2.0.0 (2023-12-12)**

  * Библиотека теперь предоставляет как синхронный, так и асинхронный API
    (см. `Введение`_ и `Справочник API`_)
  * Теперь поддерживается несколько HTTP библиотек (см.
    `Доступные реализации сессий`_ для полного списка)
  * Теперь возможно добавить поддержку любой HTTP библиотеки
    (см. `Интерфейс Session`_)
  * `requests`_ - теперь опциональная зависимость (хотя всё ещё используется
    по умолчанию для синхронного API)
  * Обратите внимание, что аргументы, специфичные для requests теперь передаются
    по другому (см. `Доступные реализации сессий`_)
  * Предпочитаемые HTTP библиотеки теперь должны быть установлены явным образом
    (см. `Введение`_)
  * :code:`Client.upload()` и :code:`Client.upload_by_link()` теперь могут
    принимать функцию, возвращающую итератор (или генератор) в качестве полезной
    нагрузки

* **Release 1.3.4 (2023-10-15)**

  * Методы :code:`upload()` и :code:`download()` (и связянные с ними) теперь
    могут загружать/скачивать файлы, не поддерживающие операцию :code:`seek()`
    (например, :code:`stdin` и :code:`stdout`, при условии, что они открыты в
    режиме :code:`"rb"` или :code:`"wb"`), см. `PR #31`_

* **Release 1.3.3 (2023-04-22)**

  * Пути вида :code:`app:/` теперь работают правильно (см. `issue #26`_)

* **Release 1.3.2 (2023-03-20)**

  * Исправлено `issue #29`_: TypeError: 'type' object is not subscriptable

* **Release 1.3.1 (2023-02-28)**

  * Исправлено `issue #28`_: :code:`TypeError` при вызове :code:`download_public()` с параметром :code:`path`
  * Исправлено :code:`AttributeError` при вызове :code:`ResourceLinkObject.public_listdir()`

* **Release 1.3.0 (2023-01-30)**

  * Добавлены convenience-методы для объектов :code:`...Object` (например, см. :code:`ResourceObject`)
  * Добавлены подсказки типов (type hints)
  * Улучшены проверки ошибок и проверка ответа
  * Добавлены :code:`InvalidResponseError`, :code:`PayloadTooLargeError`, :code:`UploadTrafficLimitExceededError`
  * Добавлено несколько недостающих полей объектов :code:`DiskInfoObject` и :code:`SystemFoldersObject`
  * Добавлены методы :code:`rename()`, :code:`upload_by_link()` и :code:`download_by_link()`
  * Добавлен аттрибут :code:`default_args` объекта :code:`YaDisk`
  * :code:`download()` и :code:`upload()` теперь возвращают :code:`ResourceLinkObject`
  * До этого возвращаемые объекты :code:`LinkObject` были заменены более конкретными подклассами
  * :code:`ConnectionError` теперь тоже вызывает повторную попытку

* **Release 1.2.19 (2023-01-20)**

  * Исправлено неправильное поведение фикса из 1.2.18 для путей :code:`disk:`
    и :code:`trash:`.

* **Release 1.2.18 (2023-01-20)**

  * Исправлено `issue #26`_: символ ':' в именах файлов приводит к
    :code:`BadRequestError`. Это поведение вызвано работой самого REST API
    Яндекс.Диска, но было исправлено на уровне библиотеки.

* **Release 1.2.17 (2022-12-11)**

  * Исправлен баг, связанный с автоматическим закрытием сессии. Использование
    метода :code:`__del__()` приводило в некоторых случаях к ошибке
    :code:`ReferenceError` (ошибка игнорировалась, но сообщение выводилось).
    Баг проявляется по большей части в старых версиях Python (например 3.4).

* **Release 1.2.16 (2022-08-17)**

  * Исправлен баг в :code:`check_token()`: функция могла вызвать :code:`ForbiddenError`,
    если у приложения недостатчно прав (`issue #23`_).

* **Release 1.2.15 (2021-12-31)**

  * Исправлено: не распознавались ссылки на асинхронные операции, если они
    использовали :code:`http://` (вместо :code:`https://`).
    Иногда Яндекс.Диск может вернуть :code:`http://` ссылку на асинхронную
    операцию. Теперь обе версии ссылок распознаются правильно, при этом,
    при получении информации об операции (через :code:`get_operation_status()`)
    всегда используется :code:`https://` версия ссылки, даже если Яндекс.Диск
    вернул :code:`http://`.

* **Release 1.2.14 (2019-03-26)**

  * Исправлена ошибка :code:`TypeError` в функциях :code:`get_public_*` при
    использовании с параметром :code:`path` (`issue #7`_)
  * Добавлен аттрибут :code:`unlimited_autoupload_enabled` для :code:`DiskInfoObject`

* **Release 1.2.13 (2019-02-23)**

  * Добавлен :code:`md5` параметр для :code:`remove()`
  * Добавлен :code:`UserPublicInfoObject`
  * Добавлен аттрибут :code:`country` для :code:`UserObject`
  * Добавлен аттрибут :code:`photoslice_time` для :code:`ResourceObject`, :code:`PublicResourceObject`
    и :code:`TrashResourceObject`

* **Release 1.2.12 (2018-10-11)**

  * Исправлен баг: не работает параметр `fields` в `listdir()` (`issue #4`_)

* **Release 1.2.11 (2018-06-30)**

  * Добавлен недостающий параметр :code:`sort` для :code:`get_meta()`
  * Добавлены аттрибуты :code:`file` и :code:`antivirus_status` для :code:`ResourceObject`,
    :code:`PublicResourceObject` и :code:`TrashResourceObject`
  * Добавлен параметр :code:`headers`
  * Исправлена опечатка в :code:`download()` и :code:`download_public()` (`issue #2`_)
  * Убран параметр :code:`*args`

* **Release 1.2.10 (2018-06-14)**

  * Исправлено поведение :code:`timeout=None`. :code:`None` должен означать „без таймаута“,
    но в предыдущих версиях значение :code:`None` было синонимично со стандартным таймаутом.

* **Release 1.2.9 (2018-04-28)**

  * Изменена лицензия на LGPLv3 (см. :code:`COPYING` и :code:`COPYING.lesser`)
  * Другие изменения информации о пакете

* **Release 1.2.8 (2018-04-17)**

  * Исправлено несколько опечаток: у :code:`PublicResourceListObject.items` и
    :code:`TrashResourceListObject.items` были неправильные типы данных
  * Псевдонимы полей в параметре :code:`fields` заменяются при выполнении
    запросов API (например, :code:`embedded` -> :code:`_embedded`)

* **Release 1.2.7 (2018-04-15)**

  * Исправлен баг перемотки файла при загрузке/скачивании после повторной попытки

* **Release 1.2.6 (2018-04-13)**

  * Теперь объекты сессий :code:`requests` кэшируются, чтобы их можно
    было переиспользовать (иногда может существенно ускорить выполнение запросов)
  * :code:`keep-alive` отключается при загрузке/скачивании файлов по умолчанию

* **Release 1.2.5 (2018-03-31)**

  * Исправлен баг (ошибка на единицу) в :code:`utils.auto_retry()` (иногда мог вызвать :code:`AttributeError`)
  * Повторные попытки применяются для :code:`upload()`, :code:`download()` и :code:`download_public()` целиком
  * Задано :code:`stream=True` для :code:`download()` и :code:`download_public()`
  * Другие мелкие исправления

* **Release 1.2.4 (2018-02-19)**

  * Исправлена опечатка (:code:`TokenObject.exprires_in` -> :code:`TokenObject.expires_in`)

* **Release 1.2.3 (2018-01-20)**

  * Исправлено :code:`TypeError` при вызове :code:`WrongResourceTypeError`

* **Release 1.2.2 (2018-01-19)**

  * :code:`refresh_token()` больше не требует валидный или пустой токен.

* **Release 1.2.1 (2018-01-14)**

  * Исправлена неработоспособность повторных попыток.

* **Release 1.2.0 (2018-01-14)**

  * Исправлено использование :code:`n_retries=0` в :code:`upload()`, :code:`download()` и :code:`download_public()`
  * :code:`upload()`, :code:`download()` и :code:`download_public()` больше не возвращают ничего (см. документацию)
  * Добавлен модуль :code:`utils` (см. документацию)
  * Добавлены :code:`RetriableYaDiskError`, :code:`WrongResourceTypeError`, :code:`BadGatewayError` и :code:`GatewayTimeoutError`
  * :code:`listdir()` теперь вызывает :code:`WrongResourceTypeError` вместо :code:`NotADirectoryError`

* **Release 1.1.1 (2017-12-29)**

  * Исправлена обработка аргументов в :code:`upload()`, :code:`download()` и :code:`download_public()`.
    До этого использование :code:`n_retries` и :code:`retry_interval` вызывало исключение (:code:`TypeError`).

* **Release 1.1.0 (2017-12-27)**

  * Усовершенствованные исключения (см. документацию)
  * Добавлена поддержка параметра :code:`force_async`
  * Мелкие исправления багов

* **Release 1.0.8 (2017-11-29)**

  * Исправлен ещё один баг в :code:`listdir()`

* **Release 1.0.7 (2017-11-04)**

  * Добавлен :code:`install_requires` в :code:`setup.py`

* **Release 1.0.6 (2017-11-04)**

  * Некоторые функции теперь возвращают :code:`OperationLinkObject`

* **Release 1.0.5 (2017-10-29)**

  * Исправлен :code:`setup.py`, теперь исключает тесты

* **Release 1.0.4 (2017-10-23)**

  * Исправлены баги в :code:`upload`, :code:`download` и :code:`listdir`
  * Значение по-умолчанию :code:`limit` в :code:`listdir` установлено в :code:`10000`

* **Release 1.0.3 (2017-10-22)**

  * Добавлен модуль :code:`settings`

* **Release 1.0.2 (2017-10-19)**

  * Исправлена функция :code:`get_code_url` (добавлены недостающие параметры)

* **Release 1.0.1 (2017-10-18)**

  * Исправлен серьёзный баг в :code:`GetTokenRequest` (добавлен недостающий параметр)

* **Release 1.0.0 (2017-10-18)**

  * Первый релиз
