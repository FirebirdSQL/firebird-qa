#coding:utf-8
#
# id:           bugs.core_3373
# title:        It is possible to store string with lenght 31 chars into column varchar(25)
# decription:   
# tracker_id:   CORE-3373
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t1(c varchar(25));
    recreate table t2(c varchar(25));
    commit;

    set term ^;
    execute block as
    begin
        execute statement 'drop domain dm_vc25';
    when any do 
        begin end
    end
    ^
    set term ;^
    commit;

    create domain dm_vc25 varchar(25) character set utf8;
    commit;
    recreate table t2(c dm_vc25);
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set count on;
    set echo on;
    insert into t1(c) values ('1234567890123456789012345xxxxxx');
    insert into t2(c) values ('1234567890123456789012345xxxxxx');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    insert into t1(c) values ('1234567890123456789012345xxxxxx');
    Records affected: 0
    insert into t2(c) values ('1234567890123456789012345xxxxxx');
    Records affected: 0
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22001
    arithmetic exception, numeric overflow, or string truncation
    -string right truncation
    -expected length 25, actual 31
    Statement failed, SQLSTATE = 22001
    arithmetic exception, numeric overflow, or string truncation
    -string right truncation
    -expected length 25, actual 31
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

