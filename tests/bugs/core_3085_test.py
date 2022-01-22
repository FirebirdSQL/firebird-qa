#coding:utf-8

"""
ID:          issue-3464
ISSUE:       3464
TITLE:       Add clause ALTER DOMAIN <name> {DROP | SET} NOT NULL
DESCRIPTION:
JIRA:        CORE-3085
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create domain dm_int int;
    commit;
    create table t(x dm_int);
    commit;

    set term ^;
    create procedure p(a dm_int) returns(msg varchar(30)) as
    begin
        msg='intro proc p: a=' || coalesce(a, 'null');
        suspend;
    end
    ^
    set term ;^
    commit;

    insert into t values(1);
    insert into t values(2);
    insert into t values(3);
    commit;

    set list on;

    alter domain dm_int set not null;
    commit;

    select msg from p(null);
    update t set x=null where x=2;
    commit;

    alter domain dm_int drop not null;
    commit;

    select msg from p(null);
    update t set x=null where x=2 returning x;
    commit;

    alter domain dm_int set not null;
"""

act = isql_act('db', test_script)

expected_stdout = """
    MSG                             intro proc p: a=null
    X                               <null>
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    validation error for variable A, value "*** null ***"
    -At procedure 'P'
    Statement failed, SQLSTATE = 23000
    validation error for column "T"."X", value "*** null ***"
    Statement failed, SQLSTATE = 22006
    unsuccessful metadata update
    -Cannot make field X of table T NOT NULL because there are NULLs present
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

