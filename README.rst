===========
Firebird QA
===========

This package contains:

- pytest plugin that provides support for testing the Firebird engine. It uses new Python
  driver for Firebird (firebird-driver).
- tests for Firebird engine (directory 'tests')
- files needed by tests (directories 'databases', 'files', 'backups')

Requirements: Python 3.8+, Firebird 3+

You should definitelly read the `QA suite documanetation`_ !

Quickstart
----------

1. Clone the git repository

2. Install the plugin and required dependencies by running next command from repo. directory::

   pip install -e .

3. Adjust Firebird server configuration.

   Firebird 3::

     # Required
     ExternalFileAccess = Full
     AuthServer = Srp, Legacy_Auth
     UserManager = Srp, Legacy_UserManager
     WireCrypt = Enabled

     # Recommended
     DefaultDbCachePages = 10000
     MaxUnflushedWrites = -1
     MaxUnflushedWriteTime = -1
     BugcheckAbort = 1

   Firebird 4+::

     # Required
     ExternalFileAccess = Full
     AuthServer = Srp256, Legacy_auth
     UserManager = Srp, Legacy_UserManager
     ReadConsistency = 0
     WireCrypt = Enabled
     ExtConnPoolSize = 10
     ExtConnPoolLifeTime = 10

     # Recommended
     DefaultDbCachePages = 10000
     MaxUnflushedWrites = -1
     MaxUnflushedWriteTime = -1
     BugcheckAbort = 1

3. Use pytest to run tests.

   The plugin adds next options to pytest::

      Firebird server:
         --server=SERVER       Server configuration name
         --bin-dir=PATH        Path to directory with Firebird utilities
         --protocol={xnet,inet,inet4,wnet}
                               Network protocol used for database attachments
         --runslow             Run slow tests
         --save-output         Save test std[out|err] output to files
         --skip-deselected={platform,version,any}
                               SKIP tests instead deselection
         --extend-xml          Extend XML JUnit report with additional information
         --install-terminal    Use our own terminal reporter

   To run all tests (except slow ones) against local server use next command::

      pytest --server local ./tests

  Note: If plugin fails to determine the directory with Firebird utilities (isql, gbak etc.),
        use `--bin-dir` option to specify it.

.. _QA suite documanetation: https://firebird-qa.readthedocs.io
