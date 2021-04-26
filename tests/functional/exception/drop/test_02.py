#coding:utf-8
#
# id:           functional.exception.drop.02
# title:        DROP EXCEPTION
# decription:   Create exception and SP that uses it. Then try to drop exception - this attempt must FAIL.
# tracker_id:   
# min_versions: []
# versions:     2.5.0
# qmid:         functional.exception.drop.drop_exception_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create exception exc_test 'message to show';
    commit;
    set term ^;
    create procedure sp_test as
    begin
      exception exc_test;
    end ^
    set term ;^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    drop exception exc_test;
    commit;
    set list on;
    set count on;
    select e.rdb$exception_name, d.rdb$dependent_name 
    from rdb$exceptions e join rdb$dependencies d on e.rdb$exception_name = d.rdb$depended_on_name
    where e.rdb$exception_name = upper('exc_test');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$EXCEPTION_NAME              EXC_TEST
    RDB$DEPENDENT_NAME              SP_TEST
    Records affected: 1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -EXCEPTION EXC_TEST
    -there are 1 dependencies
  """

@pytest.mark.version('>=2.5.0')
def test_02_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

