#coding:utf-8
#
# id:           bugs.core_4360
# title:        SELECT from derived table which contains GROUP BY on field with literal value returns wrong result
# decription:   
# tracker_id:   CORE-4360
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='NONE', sql_dialect=3, init=init_script_1)

test_script_1 = """
select c from( select 'a' c from rdb$database group by 'a' );
select c from( select 123 c from rdb$database group by 1 );
select c from( select dateadd(999 millisecond to timestamp '31.12.9999 23:59:59') c from rdb$database group by 1 );
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
C
======
a
           C
============
         123
                        C
=========================
9999-12-31 23:59:59.9990
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

