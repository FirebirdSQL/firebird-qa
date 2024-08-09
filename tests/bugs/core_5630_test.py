#coding:utf-8

"""
ID:          issue-5896
ISSUE:       5896
TITLE:       Can't create the shadow file
DESCRIPTION:
  Shadow file is can not be created during restore when -use_all_space option is used
JIRA:        CORE-5630
FBTEST:      bugs.core_5630
"""
import locale

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('Commit current transaction \\(y/n\\)\\?', '')])

expected_stdout_a = """
    RDB$FILE_SEQUENCE               0
    RDB$FILE_START                  0
    RDB$FILE_LENGTH                 0
    RDB$FILE_FLAGS                  1
    RDB$SHADOW_NUMBER               1
    S_HASH_BEFORE                   1499836372373901520
"""

expected_stdout_b = """
    RDB$FILE_SEQUENCE               0
    RDB$FILE_START                  0
    RDB$FILE_LENGTH                 0
    RDB$FILE_FLAGS                  1
    RDB$SHADOW_NUMBER               1
    S_HASH_AFTER                    1499836372373901520
"""

fdb_file = temp_file('core_5630.fdb')
fbk_file = temp_file('core_5630.fbk')
shd_file = temp_file('core_5630.shd')

@pytest.mark.version('>=3.0.3')
def test_1(act: Action, fdb_file: Path, fbk_file: Path, shd_file: Path):
    init_ddl = f"""
        set bail on;
        set list on;

        create database 'localhost:{fdb_file}' user {act.db.user} password '{act.db.password}';

        recreate table test(s varchar(30));
        commit;

        create or alter view v_shadow_info as
        select
             rdb$file_sequence  --           0
            ,rdb$file_start     --           0
            ,rdb$file_length    --           0
            ,rdb$file_flags     --           1
            ,rdb$shadow_number  --           1
        from rdb$files
        where lower(rdb$file_name) containing lower('core_5630.shd')
        ;

        insert into test select 'line #' || lpad(row_number()over(), 3, '0' ) from rdb$types rows 200;
        commit;

        create shadow 1 '{shd_file}';
        commit;
        set list on;
        select * from v_shadow_info;
        select hash( list(s) ) as s_hash_before from test;
        quit;
    """

    act.expected_stdout = expected_stdout_a
    act.isql(switches=['-q'], input = init_ddl, connect_db=False, combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    #
    with act.connect_server() as srv:
        srv.database.backup(database=fdb_file, backup=fbk_file)
        srv.wait()
    #
    fdb_file.unlink()
    shd_file.unlink()
    #
    act.reset()

    #-----------------------------------------------------------------------------------

    act.gbak(switches=['-c', '-use_all_space', str(fbk_file), act.get_dsn(fdb_file)])
    # Check that we have the same data in DB tables
    sql_text = """
        set list on;
        select * from v_shadow_info;
        select hash( list(s) ) as s_hash_after from test;
        """
    act.reset()

    #-----------------------------------------------------------------------------------
    act.expected_stdout = expected_stdout_b
    act.isql(switches=['-q', act.get_dsn(fdb_file)], input=sql_text, connect_db=False, combine_output = True, io_enc = locale.getpreferredencoding())

    assert act.clean_stdout == act.clean_expected_stdout
