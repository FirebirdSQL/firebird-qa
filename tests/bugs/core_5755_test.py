#coding:utf-8

"""
ID:          issue-6018
ISSUE:       6018
TITLE:       No error if the GRANT target object does not exist
DESCRIPTION:
  grant execute on proc|func|package and grant usage on sequence|exception -- still does NOT produce error/warning.
  These statements temply disabled until some additional comments in tracker.
JIRA:        CORE-5755
FBTEST:      bugs.core_5755
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table table_test(x int);
    create or alter procedure sp_test as begin end;

    set term ^;
    create or alter function fn_test returns int as
    begin
        return cast( rand()*10000 as int );
    end
    ^

    create or alter package pkg_test as
    begin
        procedure sp_foo;
    end
    ^

    recreate package body pkg_test as
    begin
        procedure sp_foo as
            declare c int;
        begin
            c = 1;
        end
    end
    ^
    set term ;^

    recreate sequence g_test;
    recreate exception x_test 'foo!';
    commit;

    grant create table to function wrong_func;

    grant select on table_test to function wrong_func;


    /************

    TEMPLY DISABLED, SEE ISSUE IN THE TICKET, 02-JUN-2018 08:20
    ===============

    grant execute on procedure sp_test to wrong_func;

    grant execute on function fn_test to wrong_func;

    grant execute on package pkg_test to wrong_func;

    grant usage on sequence g_test to wrong_func;

    grant usage on exception x_test to wrong_func;

    **************/
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Function WRONG_FUNC does not exist
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Function WRONG_FUNC does not exist
"""

@pytest.mark.version('>=3.0.4')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
