#coding:utf-8

"""
ID:          issue-7288
ISSUE:       7288
TITLE:       Server crashes when working with DSQL savepoints
DESCRIPTION:
NOTES:
    [20.02.2023] pzotov
    Confirmed crahses on 5.0.0.698
    Checked on 5.0.0.733 -- all fine.
"""
import pytest
from firebird.qa import *
from pathlib import Path

db = db_factory(do_not_create=True, do_not_drop = True)
act = python_act('db')

db_tmp = temp_file('gh_7288.tmp.fdb') # db_factory(filename='tmp_core_7288.fdb', do_not_create=True, do_not_drop = True)
#tmp_file = temp_file('gh_7288.tmp.sql')

@pytest.mark.version('>=3.0.11')
def test_1(act: Action, db_tmp: Path):

    chk_sql = f"""
        set list on;
        -- NB: do NOT use 'set bail on' here!
        create database 'localhost:{db_tmp}' user {act.db.user} password '{act.db.password}';
        savepoint A1;
        release savepoint A1 only;
        select count(*) from rdb$database;
        drop database;
        -----------------------------------------------------
        rollback;
        create database 'localhost:{db_tmp}' user {act.db.user} password '{act.db.password}';
        savepoint A1;
        savepoint A1;
        drop database;
    """

    expected_stdout = "COUNT                           1"
    act.isql(switches=['-q'], input = chk_sql, charset='utf-8', io_enc='utf-8', connect_db = False, credentials = False, combine_output = True)
    assert act.clean_stdout == expected_stdout
