#coding:utf-8
#
# id:           bugs.core_3474
# title:        Regression in joins on procedures
# decription:   
# tracker_id:   CORE-3474
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At line.*', '')]

init_script_1 = """"""

db_1 = db_factory(from_backup='employee-ods12.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    select e.emp_no emp_1, e.last_name name_1, p.proj_name proj_1
    from employee e
    left join
        ( get_emp_proj(e.emp_no) proc
          join project p on p.proj_id = proc.proj_id
        ) on 1=1
    order by 1,2,3
    rows 1;
   
    select e.emp_no emp_2, e.last_name name_2, p.proj_name proj_2
    from
        (
            employee e
            left join get_emp_proj(e.emp_no) proc on 1=1
        )
        left join project p on p.proj_id = proc.proj_id
    order by 1,2,3
    rows 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EMP_2                           2
    NAME_2                          Nelson
    PROJ_2                          <null>
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -E.EMP_NO
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

