#coding:utf-8

"""
ID:          create-database-08
TITLE:       Create database: Multi file DB
DESCRIPTION: Create database with two files.
FBTEST:      functional.database.create.08
"""

import pytest
from firebird.qa import *

db = db_factory(do_not_create=True)

act = python_act('db', substitutions=[('^.*TMP_CREATE_DB_08.F00', 'TMP_CREATE_DB_08.F00'),
                                      ('[ ]+', '\t')])

expected_stdout = """
    TMP_CREATE_DB_08.F00
    RDB$FILE_SEQUENCE     1
    RDB$FILE_START        201
    RDB$FILE_LENGTH       200
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    script = f"""
    create database '{act.db.dsn}' user '{act.db.user}'
      password '{act.db.password}' LENGTH 200
      FILE '{act.db.db_path.with_name('TMP_CREATE_DB_08.F00')}' LENGTH 200
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
    act.isql(switches=[], input=script, connect_db=False)
    assert act.clean_stdout == act.clean_expected_stdout
