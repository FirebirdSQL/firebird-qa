#coding:utf-8
#
# id:           bugs.core_4252
# title:        Add table name to text of validation contraint error message, to help identify error context
# decription:   
# tracker_id:   CORE-4252
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = [('line:.*', ''), ('col:.*', '')]

init_script_1 = """
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

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    show table t1;
    show table "T2";
    execute procedure sp_test(1);
    execute procedure sp_test(2);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               INTEGER Not Null
    X                               INTEGER Not Null
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    validation error for column "T1"."X", value "*** null ***"
    -At procedure 'SP_TEST' line: 3, col: 26
    Statement failed, SQLSTATE = 23000
    validation error for column "T2"."X", value "*** null ***"
    -At procedure 'SP_TEST' line: 4, col: 8
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

