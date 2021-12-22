#coding:utf-8
#
# id:           bugs.core_3085
# title:        Add clause ALTER DOMAIN <name> {DROP | SET} NOT NULL
# decription:   
# tracker_id:   CORE-3085
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             intro proc p: a=null
    X                               <null>
"""
expected_stderr_1 = """
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

