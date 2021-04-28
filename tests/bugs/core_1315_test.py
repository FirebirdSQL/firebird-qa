#coding:utf-8
#
# id:           bugs.core_1315
# title:        Data type unknown
# decription:   
# tracker_id:   CORE-1315
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1315

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# cur = db_conn.cursor()
#  try:
#    statement = cur.prep('select coalesce(?,1) from RDB$DATABASE')
#  except Exception,e:
#    print ('Failed!',e)
#  else:
#    cur.execute(statement,[2])
#    printData(cur)
#    print()
#    cur.execute(statement,[None])
#    printData(cur)
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """COALESCE
-----------
2

COALESCE
-----------
1
"""

@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


