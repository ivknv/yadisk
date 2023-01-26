��          �               �      �   �   
  �   �     O     \  �   x  3   5  f  i     �  �   �  I   x  *   �  
  �  �  �     �  9  �  �  
  #   �  X   �  �   K  9     �  S  R   �  �   O  y   -  t   �  �     ...and more. For whatever reason, files with specific extensions take much longer time to upload. Here are some known extensions with this problem: If you experience low upload speeds on Windows, the reason might be due to Python's standard library internally using :code:`select()` to wait for sockets. There are several ways around it: Known Issues Low Upload Speed on Windows Monkey-patching `http.client`_ and `urllib3`_ to use bigger :code:`blocksize`. See `this comment <https://github.com/urllib3/urllib3/issues/1394#issuecomment-954044006>`_ for more details. Monkey-patching through a library like `eventlet`_. The only known workaround is to upload files with changed filename extensions (or without them entirely). For example, if you want to upload a file named "my_database.db", you can initially upload it under the name "my_database.some_other_extension" and then rename it back to "my_database.db". This approach has some obvious downsides but at least it works. Upload Timeout on Large Files Uploading files to direct links (obtained through :any:`yadisk.YaDisk.get_upload_link()`) using a different library (such as `aiohttp`_). Using `yadisk-async`_ instead. It uses `aiohttp`_ instead of `requests`_. Very Slow Upload of Certain Types of Files When uploading large files (over a couple of GB in size) you may experience timeout errors after the full upload. This might be caused by Yandex.Disk computing hash sums or doing some other operations. The bigger the file, the bigger the timeouts may need to be set. Project-Id-Version: YaDisk 1.2.19
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2023-01-27 03:39+0500
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: ru
Language-Team: ru <LL@li.org>
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.11.0
 ...и другие. По неизвестной причине файлы с определенными расширениями в имени загружаются на Яндекс.Диск гораздо медленнее. Вот некоторые из известных проблемных расширений файлов: Если вы столкнулись с низкой скоростью загрузки файлов на Диск под Windows, то причиной может стандартная библиотека Python, которая внутри использует :code:`select()` для ожидания сокетов. В таком случае существует несколько путей обхода данной проблемы: Известные проблемы Низкая скорость загрузки файлов на Диск под Windows Monkey-patch `http.client`_ и `urllib3`_, чтобы увеличить :code:`blocksize`. См. `этот комментарий <https://github.com/urllib3/urllib3/issues/1394#issuecomment-954044006>`_. Monkey-patch через библиотеку `eventlet`_. Единственный известный способ обхода данной проблемы - это загрузка файлов с измененным расширением (или без расширения). Например, если вы хотите загрузить на Диск файл "my_database.db", вы можете изначально загрузить его под именем "my_database.some_other_extension" и после загрузки переименовать обратно в "my_database.db". У такого подхода есть очевидные недостатки, но по крайней мере он работает. Таймауты при загрузки больших файлов на Диск Загрузка файлов по прямым ссылкам (полученным через :any:`yadisk.YaDisk.get_upload_link()`), используя другую библиотеку (например, `aiohttp`_). Использование `yadisk-async`_. Эта версия использует `aiohttp`_ вместо `requests`_. Очень медленная загрузка некоторых типов файлов на Яндекс.Диск При загрузке больших файлов на Диск (несколько ГБ и более) вы можете столкнуться с таймаутами после загрузки содержимого файла на Диск. Возможно, это связано с вычислением хэш сумм и выполнением каких-то других операций. Чем больше файл, тем больше следует поставить таймаут. 