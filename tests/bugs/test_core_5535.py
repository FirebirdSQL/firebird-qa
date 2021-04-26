#coding:utf-8
#
# id:           bugs.core_5535
# title:        Garbage value in RDB$FIELD_SUB_TYPE in RDB$FUNCTION_ARGUMENTS after altering function
# decription:   
# tracker_id:   CORE-5535
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter view v_check as
    select rdb$field_sub_type from rdb$function_arguments where rdb$function_name=upper('test')
    ;
    commit;

    set list on;
    set count on;

    select * from v_check;

    create function test(i int) returns int as begin end;
    commit;
    select * from v_check;

    create or alter function test(i int) returns int as begin end;
    commit;
    select * from v_check;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
    RDB$FIELD_SUB_TYPE              <null>
    RDB$FIELD_SUB_TYPE              <null>
    Records affected: 2
    RDB$FIELD_SUB_TYPE              <null>
    RDB$FIELD_SUB_TYPE              <null>
    Records affected: 2
  """

@pytest.mark.version('>=3.0.2')
def test_core_5535_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

