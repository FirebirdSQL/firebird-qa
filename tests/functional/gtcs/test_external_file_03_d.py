#coding:utf-8

"""
ID:          n/a
FBTEST:      functional.gtcs.external_file_03_d
TITLE:       Ability to use external table with field of SMALLINT datatype
DESCRIPTION:
    Original test see in:
    https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/EXT_REL_0_3_D.script
NOTES:
    [10.09.2026] zcode.ai
    1. Re-implemented: avoid usage of temp_file() as storage for external table.
       Instead, test uses ConfigManager class from QA-plugin in order to preserve
       original content of databases.conf and restore it at the teardown stage
       (see sibling tests external_file_access_allowed_test.py, core_2796_test.py,
       core_2475_test.py and core_0116_test.py which were re-implemented in the same way).
       Copy of $FB_HOME/databases.conf will be stored in the folder where test database lives.
       New content of this file will define alias that points to test DB file
       (see 'CONNECT_TO_ALIAS') and parameter for enabling creation of
       external table which storage is in the same folder as test DB uses:
           ExternalFileAccess = Restrict {test_db_path}
       isql connects to this ALIAS with 'localhost:' prefix (remote protocol).
    2. One need to be sure that firebird.conf does NOT contain DatabaseAccess = None.
    3. The firebird.conf must contain 'ExternalFileAccess = None'.

    [12.09.2026] pzotov
    Test has been replaced with functional/table/external/external_file_all_datatypes_test.py
    Execution DISABLED.
"""

from pathlib import Path
import pytest
from firebird.qa import *

# Name of alias that will be written into temporary replacement of databases.conf:
CONNECT_TO_ALIAS = 'tmp_gtcs_external_file_03_d_alias'

# name of external table that will be used in SQL statements:
EXT_TABLE_NAME = 'ext_table'

db = db_factory()
act = python_act('db', substitutions=[('[ \t]+', ' '), ('(INPUT|OUTPUT)\\s+message .*', ''), (':\\s+(name:|table:)\\s+.*', '') ])

@pytest.mark.skip('Not needed anymore. See functional/table/external/test_external_file_all_datatypes.py')
@pytest.mark.version('>=3.0')
def test_1(act: Action, store_config: ConfigManager):

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

    # Storage of external table will be in the SAME directory as test DB uses:
    ext_file = test_db_path / 'tmp_gtcs_external_file_03_d.dat'

    # Remove leftovers from an interrupted/failed previous test run.
    ext_file.unlink(missing_ok=True)

    external_file = str(ext_file).replace("'", "''")

    test_script = f"""
        set bail on;
        set list on;
        set count on;
        connect 'localhost:{CONNECT_TO_ALIAS}' user {act.db.user} password '{act.db.password}';
        create table {EXT_TABLE_NAME} external file '{external_file}' (f01 smallint);
        commit;

        -- All subsequent statements must PASS:
        insert into {EXT_TABLE_NAME} (f01) values ( 32767);
        insert into {EXT_TABLE_NAME} (f01) values (-32768);
        insert into {EXT_TABLE_NAME} (f01) values (1);
        insert into {EXT_TABLE_NAME} (f01) values (-1);
        insert into {EXT_TABLE_NAME} (f01) values (0);

        -- All subsequent statements must FAIL:
        set bail off;
        insert into {EXT_TABLE_NAME} (f01) values ( 32768);
        insert into {EXT_TABLE_NAME} (f01) values (-32769);
        insert into {EXT_TABLE_NAME} (f01) values (0xF0000000);  -- -268435456
        insert into {EXT_TABLE_NAME} (f01) values (0x0F0000000); -- 4026531840
        commit;

        set sqlda_display on;
        select * from {EXT_TABLE_NAME} order by f01;
        commit;
        drop table {EXT_TABLE_NAME};
        exit;
    """

    act.expected_stdout = """
        Records affected: 1
        Records affected: 1
        Records affected: 1
        Records affected: 1
        Records affected: 1
        
        Statement failed, SQLSTATE = 22003
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        Records affected: 0
        
        Statement failed, SQLSTATE = 22003
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        Records affected: 0
        
        Statement failed, SQLSTATE = 22003
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        Records affected: 0
        
        Statement failed, SQLSTATE = 22003
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        Records affected: 0
        
        01: sqltype: 500 SHORT Nullable scale: 0 subtype: 0 len: 2
        F01 -32768
        F01 -1
        F01 0
        F01 1
        F01 32767
        Records affected: 5
    """
    act.isql(switches=['-q'], connect_db = False, credentials = False, input = test_script, combine_output = True )
    ext_file.unlink(missing_ok = True)
    assert act.clean_stdout == act.clean_expected_stdout
