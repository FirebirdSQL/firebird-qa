#coding:utf-8
#
# id:           bugs.core_4634
# title:        Regression: ORDER BY via an index + WHERE clause: error "no current record for fetch operation"
# decription:   
# tracker_id:   CORE-4634
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
    -- Confirmed for WI-T3.0.0.31374 Firebird 3.0 Beta 1:
    -- Statement failed, SQLSTATE = 22000
    -- no current record for fetch operation
    set list on;
    select *
    from sales
    where (order_status like '1%' or order_status like '%1%')
    order by order_status
    rows 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_4634_1(act_1: Action):
    act_1.execute()

