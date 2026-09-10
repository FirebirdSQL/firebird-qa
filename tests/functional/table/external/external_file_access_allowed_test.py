#coding:utf-8

"""
ID:          https://github.com/FirebirdSQL/firebird/pull/9121
TITLE:       External table must be allowed in in the directory belonging to the list specified in the 'ExternalFileAccess' config parameter
DESCRIPTION:
    https://github.com/FirebirdSQL/firebird-qa/pull/39
    Regression test for external file path validation at *** METADATA LOAD *** time.

    When ExternalFileAccess is restricted to the directory containing the test database, an external table whose file is located inside that
    directory must still work normally.
NOTES:
    [10.09.2026] pzotov
    1. Re-implemented: avoid usage of $QA_ROOT/files/qa-databases.conf (suggested by Anton Zuev, RedBase).
       Test uses ConfigManager class from QA-plugin in order to preserve original content of databases.conf and restore it at the teardown stage.
       Copy of $FB_HOME/databases.conf will be stored in the folder where test database lives.
       New content of this file will define alias that points to test DB file (see 'CONNECT_TO_ALIAS') and parameter for enabling creation of
       external table which storage is in the same folder as test DB uses:
           ExternalFileAccess = Restrict {test_db_path}

    2. The firebird.conf must contain 'ExternalFileAccess = None'. Some old tests have to be re-implemented because of this change.

    ###############
    ### ACHTUNG ###
    ###############
    CURRENTLY TEST PASSES BUT ALL MAJOR VERSIONS BEHAVE NOT LIKE IT IS DESIRED BY THIS PULL REQUEST #39:
    ACCESS CHECK IS PERFORMED ONLY DURING DML RATHER THAN DDL. WAITING FOR FIX #9121.

    Checked on 6.0.0.2169; 5.0.5.1879; 4.0.8.3314; 3.0.15.33884  
"""

from pathlib import Path
import time
import pytest
from firebird.qa import *

# Name of alias that will be written into temporary replacement of databases.conf:
CONNECT_TO_ALIAS = 'tmp_external_file_allowed_alias'

# name of external table that will be used in SQL statements:
EXT_TABLE_NAME = 'ext_allowed'

db = db_factory()
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

tmp_file = temp_file('func-extfile-access-allowed.copy')

@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_file: Path, store_config: ConfigManager, capsys):

    # Obtain the physical database location.
    # NOTE: we must NOT use 'act.db.db_path' for ALIASED databases! It will return '.' rather than full path+filename.
    # Use only con.info.name for that:
    TEMP_DB_CONF_CONTENT = ''
    with act.db.connect() as con:
        test_db_file = con.info.name
        test_db_path = Path(test_db_file).parent
        TEMP_DB_CONF_CONTENT = f"""
            {CONNECT_TO_ALIAS} = {test_db_file}
            {{
                ExternalFileAccess = Restrict {test_db_path}
            }}
        """
    assert CONNECT_TO_ALIAS in TEMP_DB_CONF_CONTENT and 'ExternalFileAccess' in TEMP_DB_CONF_CONTENT

    # REPLACE databases.conf:
    store_config.replace('databases.conf', TEMP_DB_CONF_CONTENT)

    allowed_file = test_db_path / 'ext_access_allowed_test.dat'

    # Remove leftovers from an interrupted/failed previous test run.
    allowed_file.unlink(missing_ok=True)

    external_file = str(allowed_file).replace("'", "''")

    test_sql = f"""
        set bail on;
        set list on;
        connect 'localhost:{CONNECT_TO_ALIAS}' user {act.db.user} password '{act.db.password}';
        create table {EXT_TABLE_NAME} external file '{external_file}'(letter char(1), lf char(1));
        commit;
        set count on;
        select rdb$relation_name, rdb$relation_type from rdb$relations where upper(rdb$relation_name) = upper('{EXT_TABLE_NAME}');
        insert into {EXT_TABLE_NAME}(letter, lf) select ascii_char(64+i), ascii_char(10) from (select row_number()over() as i from rdb$types rows 5);
        commit;
        select letter from {EXT_TABLE_NAME};
        commit;
        drop table {EXT_TABLE_NAME};
        commit;
    """

    act.expected_stdout = f"""
        RDB$RELATION_NAME {EXT_TABLE_NAME.upper()}
        RDB$RELATION_TYPE 2
        Records affected: 1

        Records affected: 5
        
        LETTER A
        LETTER B
        LETTER C
        LETTER D
        LETTER E
        Records affected: 5
    """

    act.isql(switches=['-q'], connect_db = False, credentials = False, input = test_sql, combine_output = True)
    allowed_file.unlink(missing_ok = True)

    assert act.clean_stdout == act.clean_expected_stdout
