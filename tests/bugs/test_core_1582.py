#coding:utf-8
#
# id:           bugs.core_1582
# title:        ABS() rounds NUMERIC values
# decription:   
# tracker_id:   CORE-1582
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1582

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT
  ABS(CAST(-1.98 AS NUMERIC(10,2))),
  ABS(CAST(-1.23 AS DECIMAL(10,2))),
  ABS(CAST(-1.98 AS NUMERIC(9,2))),
  ABS(CAST(-1.23 AS DECIMAL(9,2)))
  FROM RDB$DATABASE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                  ABS                   ABS                   ABS                   ABS
===================== ===================== ===================== =====================
                 1.98                  1.23                  1.98                  1.23

"""

@pytest.mark.version('>=2.1')
def test_core_1582_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

