#coding:utf-8

"""
ID:          issue-4873
ISSUE:       4873
TITLE:       DDL trigger remains active after dropped
DESCRIPTION:
JIRA:        CORE-4555
FBTEST:      bugs.core_4555
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create exception ddl_exception 'You have no right to create exceptions. Learn DDL triggers first!';
    commit;
    set term ^;
    create or alter trigger t_ddl
    active before create exception
    as
    begin
      if (current_user <> 'DUDE') then
        exception ddl_exception;
    end
    ^
    set term ;^
    commit;

    create exception user_exception 'Invalid remainder found for case-1.';
    commit;

    drop trigger t_ddl;
    commit;

    create exception user_exception 'Invalid remainder found for case-2.'
    ;
    commit;

    set list on;
    set count on;
    select rdb$exception_name, rdb$message
    from rdb$exceptions
    order by rdb$exception_name;
"""

act = isql_act('db', test_script, substitutions=[('=.*', ''), ('line:\\s[0-9]+,', 'line: x'),
                                                 ('col:\\s[0-9]+', 'col: y')])

expected_stdout = """
    RDB$EXCEPTION_NAME              DDL_EXCEPTION
    RDB$MESSAGE                     You have no right to create exceptions. Learn DDL triggers first!

    RDB$EXCEPTION_NAME              USER_EXCEPTION
    RDB$MESSAGE                     Invalid remainder found for case-2.

    Records affected: 2
"""

expected_stderr = """
    Statement failed, SQLSTATE = HY000
    unsuccessful metadata update
    -CREATE EXCEPTION USER_EXCEPTION failed
    -exception 1
    -DDL_EXCEPTION
    -You have no right to create exceptions. Learn DDL triggers first!
    -At trigger 'T_DDL' line: 6, col: 9
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

