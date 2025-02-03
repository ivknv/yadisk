Contributing
============

.. contents:: Table of contents

Bug reports, feedback, questions, feature requests, etc.
********************************************************

If you've found a bug, have some questions, a feature request, or some other
form of feedback, feel free to `open an issue
<https://github.com/ivknv/yadisk/issues>`_, use the appropriate template.

Issues are accepted in 2 languages: English or Russian, whichever is more
comfortable.

Pull requests
*************

Pull requests are also welcome, however, be prepared to have your PR rejected,
since some changes might not be appropriate for this project.

If you would like to contribute a PR, keep the following in mind:

#. This is a general-purpose API client library meant for developers, not an end-user
   tool
#. The main goal of this library is to provide simple, convenient and reliable
   access to the Yandex.Disk's REST API, mostly mirroring it
#. Reliability and correctness are valued above API convenience
#. Some changes may seem useful but may also end up inadvertently creating edge
   cases, making the feature unreliable or complicated to use safely. See if
   that's the case for your PR.
#. Tests are appreciated but not necessary for the initial PR, they can be
   added later by this repository's maintainer
#. There is quite a lot of code duplication, mostly due to implementation of both
   sync/async interfaces, beware of that

If you're unsure if your PR can make it into the repository, consider opening
an issue instead.

Here are some PR examples that are likely to be merged:

* Bug fixes
* New/enhanced tests (that cover something that isn't adequately tested at the moment)
* Documentation (e.g, added examples, corrections, additional REST API insight)
* Support for an HTTP library (see Sessions and Session Interface in the documentation)

Pull request workflow
---------------------

The pull request workflow looks as follows:

#. Fork the repository
#. Create a new branch with a unique name, specific to your PR, use the :code:`dev`
   branch as the starting point
#. Run linting tools
#. Run tests
#. If everything is good, commit changes
#. Push to your forked repository
#. Submit a pull request, set :code:`dev` as the destination branch

Branch structure
****************

The :code:`master` branch is used for stable releases, while the :code:`dev`
branch is used for work in progress. All changes have to go through the
:code:`dev` branch before being merged into :code:`master`.

Setting up the development environment
**************************************

Assuming you already have the appropriate Python version installed, first,
setup the virtualenv:

.. code:: bash

   # Optional: use .venv/$PYTHON_VERSION to manage venvs for multiple Python versions
   python3 -m venv .venv

After setting up the virtualenv you can activate it and install all the
development dependencies and tools:

.. code:: bash

   # Enter the created virtual environment
   source .venv/bin/activate

   # Now install development dependencies and tools (requirements-dev.txt)
   # as well as tools needed to build the documentation (docs/requirements.txt)
   pip install -r requirements-dev.txt -r docs/requirements.txt

Linting
*******

Before committing changes run linting tools and fix reported errors:

.. code:: bash

   ruff check
   mypy

Both :code:`ruff` and :code:`mypy` are configured in :code:`pyproject.toml`.

Testing
*******

Traffic recording / traffic replay
----------------------------------

Testing the API client has several challenges:

* Sometimes the servers may be unavailable or simply malfunction
* Sending requests takes a very long time
* It is possible to hit a quota for certain functions in the process
* Have to use a real user account
* Cloud storage is persistent, so it has to be repeatedly cleaned up
* There is a risk of data loss due to bugs or misconfiguration

This makes it unsuitable for continuous integration. However, we can record
real traffic and then replay it in tests to solve all of the above problems at
once. An **API gateway** is used for this purpose. It's a simple HTTP server
(see :code:`tests/disk_gateway.py`), that can either **relay** all the requests
to the actual Yandex.Disk servers while **recording** them to a JSON file, or
**replay** them from a recorded JSON file without actually sending them
anywhere. Of course, it is still necessary to occasionally re-record them,
since the actual API behavior may change over time.

Configuration
-------------

In order to run most tests you need to configure a set of environment variables:

.. code:: bash

   export PYTHON_YADISK_APP_ID='<your test application ID>'
   export PYTHON_YADISK_APP_SECRET='<your test application secret>'
   export PYTHON_YADISK_APP_TOKEN='<currently valid access token for your test application>'
   export PYTHON_YADISK_TEST_ROOT='<path to the directory where all tests will be contained>'
   export PYTHON_YADISK_REPLAY_ENABLED='<0 or 1 (default), 0 disables traffic replay, 1 enables it>'
   export PYTHON_YADISK_RECORDING_ENABLED='<0 (default) or 1, 1 enables traffic recording, 0 disables it>'
   export PYTHON_YADISK_GATEWAY_HOST='<127.0.0.1 by default, host for the test API gateway>'
   export PYTHON_YADISK_GATEWAY_PORT='<8080 by default, port for the test API gateway>'


.. note::

   Be very careful with the location of :code:`PYTHON_YADISK_TEST_ROOT`.
   Specifing the wrong directory may lead to **permanent loss of data in
   that folder**.

.. note::

   :code:`PYTHON_YADISK_APP_ID` and :code:`PYTHON_YADISK_APP_SECRET` are only
   used in some authentication/authorization tests (see
   :code:`tests/test_auth.py`), during replays they **do not have to be
   valid**, they only need to be valid at the time of recording of these tests
   (although they still **have to match**). In fact, if you ever find yourself
   recording tests that use :code:`PYTHON_YADISK_APP_SECRET`, make sure to
   **generate a new application secret** afterwards.

Replaying tests
---------------

Testing is done with :code:`pytest`.
To only **replay**, set :code:`PYTHON_YADISK_RECORDING_ENABLED=0` and
:code:`PYTHON_YADISK_REPLAY_ENABLED=1` (this is the default behavior):

.. code:: bash

   pytest -vx tests
   # or the same thing more explicitly
   PYTHON_YADISK_RECORDING_ENABLED=0 PYTHON_YADISK_REPLAY_ENABLED=1 pytest -vx tests

.. note::

   Running tests in replay mode will only work if :code:`PYTHON_YADISK_APP_ID`,
   :code:`PYTHON_YADISK_APP_SECRET` and :code:`PYTHON_YADISK_TEST_ROOT` all
   match with those at the time of recording. :code:`PYTHON_YADISK_APP_TOKEN`
   is not stored anywhere and doesn't need to be valid nor match the value at
   the time of recording.

Environment variables, necessary for running replays of the recorded tests
are provided in the :code:`tests/.env` file. Note that the secret in that file
is not actually valid.

Recording tests
---------------

To **record** tests, set :code:`PYTHON_YADISK_RECORDING_ENABLED=1` and
:code:`PYTHON_YADISK_REPLAY_ENABLED=0`:

.. code:: bash

   PYTHON_YADISK_RECORDING_ENABLED=1 PYTHON_YADISK_REPLAY_ENABLED=0 pytest -vx tests

The recorded JSON files are stored in :code:`tests/recorded/{sync,async}`.

.. note::

   Recorded JSON files may contain **personal information**, such as your name
   and other account information (see :code:`test_get_disk_info()`), as well as
   some information about your files (see :code:`test_get_last_uploaded()`,
   :code:`test_get_public_resources()`, :code:`test_get_files()`). Inspect
   the files after recording them. Content of requests and responses is compressed
   with zlib and encoded with Base64 (see :code:`tests/disk_gateway.py`)

Running tests without either recording or replaying
---------------------------------------------------

It is also possible to run tests without recording or replay:

.. code:: bash

   PYTHON_YADISK_RECORDING_ENABLED=0 PYTHON_YADISK_REPLAY_ENABLED=0 pytest -vx tests

Documentation
*************

.. _Read the Docs (en): https://yadisk.readthedocs.io/en/latest/
.. _Read the Docs (ru): https://yadisk.readthedocs.io/ru/latest/

All documentation is written in English and then additionally localized to Russian.
Documentation is built with :code:`sphinx` and reSructuredText (:code:`.rst` files).
It is published at `Read the Docs (en)`_ and `Read the Docs (ru)`_

Building documentation
----------------------

To build the documentation in HTML
format, go the :code:`docs/` directory and run the following command:

.. code:: bash

   make html

This will build the documentation in English. The resulting files can be found
in the :code:`docs/_build/html` directory.

To build documentation in Russian, run the following command:

.. code:: bash

   make -e SPHINXOPTS='-D language=ru' html

Translation
-----------

.. _Sphinx/Internationalization: https://www.sphinx-doc.org/en/master/usage/advanced/intl.html

The translation workflow looks something like this:

#. Extract translatable messages with
   :code:`make gettext`
#. Generate :code:`.po` files with :code:`sphinx-intl update -p _build/gettext -l ru`
   (can be found in :code:`locales/ru/LC_MESSAGES`)
#. Translate :code:`.po` files
#. Build translated documentation with :code:`make -e SPHINXOPTS='-D language=ru' html`

See `Sphinx/Internationalization`_ for more instructions.

New release workflow
**********************

.. _Read the Docs (dev, en): https://yadisk.readthedocs.io/en/dev/
.. _Read the Docs (dev, ru): https://yadisk.readthedocs.io/ru/dev/

This is the general workflow for publishing a new release:

#. Commit changes to the :code:`dev` branch
#. Update documentation
#. Run tests and linting
#. Update translations
#. Push changes
#. Run tests and linting with Github Actions, ensure there are no errors
#. Check that the documentation is not broken at `Read the Docs (dev, en)`_ and `Read the Docs (dev, ru)`_
#. Bump version number in several files (follow semantic versioning):

   #. :code:`__version__` in :code:`src/yadisk/__init__.py`
   #. :code:`version` in :code:`docs/conf.py`

#. Write the release notes and translate them, put them in the following files:

   #. :code:`docs/changelog.rst`
   #. :code:`README.rst`
   #. :code:`README.en.rst`
   #. :code:`README.ru.rst`

#. Push the changes
#. Run tests and linting with Github Actions, ensure there are no errors
#. Check that the documentation is not broken at `Read the Docs (dev, en)`_ and `Read the Docs (dev, ru)`_
#. Create a PR and merge changes to :code:`master`
#. Build the package (wheel and source archive)
#. Upload the built package to PyPI
#. Add a new release on Github
