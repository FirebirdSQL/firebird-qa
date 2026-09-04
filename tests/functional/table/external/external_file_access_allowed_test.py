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
    [08.08.2026] sunliqiang
    The test database uses a dedicated databases.conf alias with
    ExternalFileAccess restricted to its database directory.

    [04.09.2026] pzotov
    1. One need to be sure that firebird.conf does NOT contain DatabaseAccess = None.
    2. Test uses pre-created databases.conf which has alias defined by variable REQUIRED_ALIAS.
       Database file for that alias must NOT exist in the QA_root/files/qa/ subdirectory: it will be created here.
       Content of databases.conf must be taken from $QA_ROOT/files/qa-databases.conf (one need to replace
       it before every test session).
       Discussed with pcisar, letters since 30-may-2022 13:48, subject:
       "new qa, core_4964_test.py: strange outcome when use... shutil.copy() // comparing to shutil.copy2()"
    3. Value of REQUIRED_ALIAS must be EXACTLY the same as alias specified in the pre-created databases.conf
       (for LINUX this equality is case-sensitive, even when aliases are compared):
       tmp_external_file_allowed_alias = $(dir_sampleDb)/qa/tmp_external_file_allowed.fdb
       {
           ExternalFileAccess = Restrict $(dir_sampleDb)/qa
       }
    4. The firebird.conf must contain 'ExternalFileAccess = None'. Some old tests have to be re-implemented because of this change.

    ###############
    ### ACHTUNG ###
    ###############
    CURRENTLY TEST PASSES BUT ALL MAJOR VERSIONS BEHAVE NOT LIKE IT IS DESIRED BY THIS PULL REQUEST #39:
    ACCESS CHECK IS PERFORMED ONLY DURING DML RATHER THAN DDL. WAITING FOR FIX.

    Checked on 6.0.0.2169; 5.0.5.1879; 4.0.8.3314; 3.0.15.33884  
"""

from pathlib import Path

import pytest
from firebird.qa import *

EXT_TABLE_NAME = 'ext_allowed'

# Pre-defined alias from QA_root/files/qa-databases.conf.
# This file must be copied manually to each testing FB home folder
# with replacing databases.conf there.
# Alias must contain 'ExternalFileAccess' parameter (per-database)
# which is specified to some directory that for sure does exist
# when this test is running. Currently it is $(dir_sampleDb)/qa,
# thus parameter looks like:
# ExternalFileAccess = Restrict $(dir_sampleDb)/qa
#
REQUIRED_ALIAS = 'tmp_external_file_allowed_alias'

db = db_factory(filename='#' + REQUIRED_ALIAS)
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.skip("Need fix #9121. Some tests must be re-implemented.")
@pytest.mark.version('>=3.0')
def test_1(act: Action):

    # The database itself is located in the directory configured in
    # ExternalFileAccess, so a sibling external file is guaranteed to
    # be inside the allowed directory.
    # Obtain the physical database location. The database is created inside the directory allowed by ExternalFileAccess.
    # NOTE: we must NOT use 'act.db.db_path' for ALIASED databases! It will return '.' rather than full path+filename.
    # Use only con.info.name for that:
    with act.db.connect() as con:
        allowed_dir = Path(con.info.name).parent
        
    allowed_file = allowed_dir / 'ext_access_allowed_test.dat'

    # Remove leftovers from an interrupted/failed previous test run.
    allowed_file.unlink(missing_ok=True)

    external_file = str(allowed_file).replace("'", "''")

    test_sql = f"""
        set bail on;
        set list on;
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

    act.isql(switches=['-q'], input = test_sql, combine_output = True)
    allowed_file.unlink(missing_ok = True)

    assert act.clean_stdout == act.clean_expected_stdout
