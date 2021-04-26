===========
Firebird QA
===========

This package contains:

- pytest plugin that provides support for testing the Firebird engine. It uses new Python
  driver for Firebird (firebird-driver).
- tests for Firebird engine (directory 'tests')
- files needed by tests (directories 'databases', 'files', 'backups')

Requirements: Python 3.8+, Firebird 3+

Usage Guide
-----------

1. Clone the git repository

2. Install the plugin and required dependencies by running next command from repo. directory::

   pip install -e .

3. Create / edit `firebird.conf` file. The default file defines `local` server with default
   SYSDBA password. You may change it or add more servers.

3. Use pytest to run tests.

   The plugin adds nex options to pytests::

      Firebird server:
        --server=SERVER       Server configuration name
        --bin-dir=PATH        Path to directory with Firebird utilities
        --protocol={xnet,inet,inet4,wnet}
                              Network protocol used for database attachments
        --runslow             Run slow tests

   To run all tests (except slow ones) against local server use next command::

      pytest --server local ./tests

  Note: If plugin fails to determine the directory with Firebird utilities (isql, gbak etc.),
        use `--bin-dir` option to specify it.

