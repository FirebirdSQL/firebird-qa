#coding:utf-8

"""
ID:          issue-4644
ISSUE:       4644
TITLE:       Regression: ISQL does not destroy the SQL statement
DESCRIPTION:
JIRA:        CORE-4321
FBTEST:      bugs.core_4321
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- NB: 2.1.7 FAILED, output contains '4' for select count(*) ...
    set list on
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    select 1 x from rdb$database;

    select count(*) c from mon$statements s
    where s.mon$sql_text containing 'select 1 x' -- 08-may-2017: need for 4.0 Classic! Currently there is also query with RDB$AUTH_MAPPING data in mon$statements
    ;
    commit;
    select count(*) c from mon$statements s
    where s.mon$sql_text containing 'select 1 x'
    ;

    select 1 x from rdb$database;
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    select 1 x from rdb$database;

    select count(*) c from mon$statements s
    where s.mon$sql_text containing 'select 1 x'
    ;
    commit;

    select count(*) c from mon$statements s
    where s.mon$sql_text containing 'select 1 x'
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
    X                               1
    X                               1
    X                               1
    C                               1
    C                               1
    X                               1
    X                               1
    X                               1
    X                               1
    C                               1
    C                               1
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

