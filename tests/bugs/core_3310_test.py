#coding:utf-8
#
# id:           bugs.core_3310
# title:        RDB$GET_CONTEXT and between in view
# decription:   
# tracker_id:   CORE-3310
# min_versions: ['3.0']
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
    create or alter view v_test
    as
    select s.po_number
    from sales s
    where 
      cast(coalesce(rdb$get_context('USER_SESSION', 'SELECTED_DATE'), '12.12.1993') as timestamp) 
      between 
      s.order_date and s.date_needed
    ;
    set list on;
    select * from v_test v order by v.po_number rows 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PO_NUMBER                       V9320630
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

