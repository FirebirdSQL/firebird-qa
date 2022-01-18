#coding:utf-8

"""
ID:          issue-939
ISSUE:       939
TITLE:       Before triggers are firing after checks
DESCRIPTION:
JIRA:        CORE-583
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test1 (i int, constraint test1_chk check (i between 1 and 5));
    commit;

    set term ^;
    create trigger test1_bi for test1 active before insert position 0 as
    begin
       new.i=6;
    end
    ^

    create trigger test1_bu for test1 active before update position 0 as
    begin
       new.i=7;
    end
    ^
    set term ;^
    commit;

    set count on;
    insert into test1 values (2);
    select * from test1;
    update test1 set i=2 where i = 6;
    select * from test1;
"""

act = isql_act('db', test_script, substitutions=[('-At trigger.*', '-At trigger')])

expected_stdout = """
    Records affected: 0
    Records affected: 0
    Records affected: 0
    Records affected: 0
"""

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    Operation violates CHECK constraint TEST1_CHK on view or table TEST1
    -At trigger 'CHECK_3'
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

