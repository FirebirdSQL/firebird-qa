#coding:utf-8

"""
ID:          issue-4576
ISSUE:       4576
TITLE:       Add table name to text of validation contraint error message, to help identify error context
DESCRIPTION:
JIRA:        CORE-4252
FBTEST:      bugs.core_4252
"""

import pytest
from firebird.qa import *

init_script = """
    create or alter procedure sp_test(a_arg smallint) as begin end;
    commit;

    recreate table t1(x int not null );
    recreate table "T2"("X" int not null );
    commit;

    set term ^;
    create or alter procedure sp_test(a_arg smallint) as
    begin
      if  ( a_arg = 1 ) then insert into t1(x) values(null);
      else insert into "T2"("X") values(null);
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    show table t1;
    show table "T2";
    execute procedure sp_test(1);
    execute procedure sp_test(2);
"""

act = isql_act('db', test_script, substitutions=[('line:.*', ''), ('col:.*', '')])

expected_stdout = """
    X                               INTEGER Not Null
    X                               INTEGER Not Null
"""

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    validation error for column "T1"."X", value "*** null ***"
    -At procedure 'SP_TEST' line: 3, col: 26
    Statement failed, SQLSTATE = 23000
    validation error for column "T2"."X", value "*** null ***"
    -At procedure 'SP_TEST' line: 4, col: 8
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
