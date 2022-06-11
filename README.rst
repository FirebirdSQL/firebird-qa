===========
Firebird QA
===========

This package contains:

- pytest plugin that provides support for testing the Firebird engine. It uses new Python
  driver for Firebird (firebird-driver).
- tests for Firebird engine (directory 'tests')
- files needed by tests (directories 'databases', 'files', 'backups')

Requirements: Python 3.8+, Firebird 3+

You should definitelly read the `QA suite documentation`_ !

Quickstart
----------

1. Clone the git repository

2. Install the plugin and required dependencies by running next command from repo. directory::

   pip install -e .

3. Adjust Firebird server configuration.

3.1. $FB_HOME/firebird.conf::

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

     # Needed for encryption-related tests:
     KeyHolderPlugin = fbSampleKeyHolder

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

     # Needed for encryption-related tests:
     KeyHolderPlugin = fbSampleKeyHolder

3.2. Required changes for running encryption-related tests::

     3.2.1. Change dir to $FB_HOME/examples/prebuilt/plugins/ and make copy of following files into $FB_HOME/plugins/ ::

         3.2.1.1. Configs::
             fbSampleKeyHolder.conf
             fbSampleDbCrypt.conf

         3.2.1.2. Binaries on Windows::
             fbSampleDbCrypt.dll
             fbSampleKeyHolder.dll

         3.2.1.3. Binaries on Linux::
             libfbSampleDbCrypt.so
             libfbSampleKeyHolder.so

         # NOTE.
         # These files present only in Firebird 4.x+ snapshots. 
         # They missed in Firebird 3.x but they can be used there.

     3.2.2. In $FB_HOME/plugins/fbSampleKeyHolder.conf::

         Auto = true
         KeyRed=111
         KeyGreen = 119

     3.2.3. In $FB_HOME/plugins/fbSampleDbCrypt.conf::

         # Encure that Auto = false or just is commented out

     3.3.3. Restart Firebird and check that all set correct. Example for Linux:

         shell rm -f /var/tmp/tmp4test.fdb;
         create database 'localhost:/var/tmp/tmp4test.fdb' user sysdba password 'masterkey';


         -- Following must PASS:

         set echo on;
         set bail on;
         alter database encrypt with "fbSampleDbCrypt" key Red;
         shell sleep 2;

         alter database decrypt;
         shell sleep 2;

         alter database encrypt with "fbSampleDbCrypt" key Green;
         shell sleep 2;

         alter database decrypt;
         shell sleep 2;

         set echo off;
         set bail off;

         -- Following must FAIL with:
         -- Statement failed, SQLSTATE = 42000
         -- unsuccessful metadata update
         -- -ALTER DATABASE failed
         -- -Missing correct crypt key
         -- -Plugin fbSampleKeyHolder:
         -- -Crypt key NOSUCH not set

         set echo on;
         alter database encrypt with "fbSampleDbCrypt" key NoSuch;
         shell sleep 2;

         show database;
         quit;


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

.. _QA suite documentation: https://firebird-qa.readthedocs.io
