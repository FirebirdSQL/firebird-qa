#coding:utf-8
#
# id:           bugs.core_0583
# title:        before triggers are firing after checks
# decription:   
#                
# tracker_id:   CORE-583
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('-At trigger.*', '-At trigger')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
    Records affected: 0
    Records affected: 0
    Records affected: 0
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    Operation violates CHECK constraint TEST1_CHK on view or table TEST1
    -At trigger 'CHECK_3'
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

