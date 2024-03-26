#coding:utf-8

"""
ID:          issue-7937
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7937
TITLE:       Inner join raises error "no current record for fetch operation" if a stored procedure depends on some table via input parameter and also has an indexed relationship with another table
DESCRIPTION:
NOTES:
    [26.03.2024] pzotov
    Confirmed bug on 5.0.0.1305, 6.0.0.279
    Checked on 6.0.0.286 -- all OK.
    Thanks to dimitr for providing simplest test case.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    create table test (id int primary key);
    insert into test values (1);
    commit;
    set term ^;
    create procedure sp_test (p int) returns (r int)
    as begin
       r = 1;
       suspend;
    end^
    set term ;^
    commit;
    select count(*)
    from test
    inner join sp_test(test.id) on sp_test.r = test.id;
"""

act = isql_act('db', test_script, substitutions=[('[ \t]+', ' ')])

expected_stdout = """
    COUNT 1
"""

@pytest.mark.version('>=6.0.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
