#coding:utf-8

"""
ID:          n/a
ISSUE:       None
TITLE:       LTT. Regression with SAVEPOINTS.
DESCRIPTION:
    Test is based on example provided by Adriano privately.
NOTES:
    [11.04.2026] pzotov
    Letter from Adriano: 27.02.2026 13:25 +0300.
    Confirmed bug (regression) on 6.0.0.1789-c3d5f12.
    Checked on 6.0.0.1794-03fed18.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    set autoddl off;
    
    create local temporary table ltt_svp (id int) on commit preserve rows;
    commit retain;

    savepoint sp1;
    alter table ltt_svp add col1 int;

    savepoint sp2;
    alter table ltt_svp add col2 int;

    rollback to savepoint sp2;

    savepoint sp3;
    alter table ltt_svp add col3 int;

    release savepoint sp3;
    rollback to savepoint sp1;

    alter table ltt_svp add col4 int;
    commit retain;

    set bail OFF;
    -- Things starts to be different here

    select col1 from ltt_svp;

    select col2 from ltt_svp;

    select col3 from ltt_svp;

    insert into ltt_svp (id, col4) values (5, 40);

    set count on;
    select * from ltt_svp order by id;

"""

substitutions = [('[ \t]+', ' '), ('(-)?At line \\d+.*', '')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -"COL1"

    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -"COL2"

    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -"COL3"

    ID 5
    COL4 40
    Records affected: 1
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
