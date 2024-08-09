#coding:utf-8

"""
ID:          create-database-10
TITLE:       Create database: Multi file DB - starting
DESCRIPTION: Database with four files. Additional files specified by STARTING AT.
FBTEST:      functional.database.create.10
"""

import pytest
from firebird.qa import *

db = db_factory(do_not_create=True)

act = python_act('db', substitutions=[('^.*TMP_CREATE_DB_10.F0', 'TMP_CREATE_DB_10.F0'), ('[ ]+', '\t')])

expected_stdout = """
    TMP_CREATE_DB_10.F00
    RDB$FILE_SEQUENCE     1
    RDB$FILE_START        301
    RDB$FILE_LENGTH       300
    TMP_CREATE_DB_10.F01
    RDB$FILE_SEQUENCE     2
    RDB$FILE_START        601
    RDB$FILE_LENGTH       400
    TMP_CREATE_DB_10.F02
    RDB$FILE_SEQUENCE     3
    RDB$FILE_START        1001
    RDB$FILE_LENGTH       0
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    script = f"""
    create database '{act.db.dsn}' user '{act.db.user}'
      password '{act.db.password}'
      FILE '{act.db.db_path.with_name('TMP_CREATE_DB_10.F00')}' STARTING AT PAGE 301
      FILE '{act.db.db_path.with_name('TMP_CREATE_DB_10.F01')}' STARTING AT PAGE 601
      FILE '{act.db.db_path.with_name('TMP_CREATE_DB_10.F02')}' STARTING AT PAGE 1001
    ;
    set list on ;
    select
        cast(rdb$file_name as varchar(100)) db_file
        ,rdb$file_sequence
        ,rdb$file_start
        ,rdb$file_length
    from rdb$files ;
    """
    act.expected_stdout = expected_stdout
    act.isql(switches = ['-q'], input=script, connect_db=False, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
