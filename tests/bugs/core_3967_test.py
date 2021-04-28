#coding:utf-8
#
# id:           bugs.core_3967
# title:        subselect with reference to outer select fails
# decription:   
# tracker_id:   CORE-3967
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='employee-ods12.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    select r1.rdb$relation_name rel_name
    from rdb$relation_fields f1
    join rdb$relations r1 on f1.rdb$relation_name = r1.rdb$relation_name
    where
        f1.rdb$field_name = upper('emp_no') and
        not exists(
            select r2.rdb$relation_name
            from rdb$relation_fields f2
            join rdb$relations r2 on f2.rdb$relation_name=r1.rdb$relation_name
            where f2.rdb$field_name = upper('phone_ext')
        )
    order by 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    REL_NAME                        EMPLOYEE_PROJECT
    REL_NAME                        SALARY_HISTORY
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

