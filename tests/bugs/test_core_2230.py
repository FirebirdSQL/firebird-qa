#coding:utf-8
#
# id:           bugs.core_2230
# title:        Implement domain check of input parameters of execute block
# decription:   
# tracker_id:   CORE-2230
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN DOM1 AS INTEGER NOT NULL CHECK (value in (0, 1));
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  cmd = c.prep('execute block (x DOM1 = ?) returns (y integer) as begin y = x; suspend; end')
#  
#  c.execute(cmd,[1])
#  printData(c)
#  
#  try:
#    c.execute(cmd,[10])
#    printData(c)
#  except kdb.DatabaseError,e:
#    print (e[0])
#  else:
#    print ('Test Failed')
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Y
-----------
1
Y
-----------
Cursor.fetchone:
- SQLCODE: -625
- validation error for variable X, value "10"
"""

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_2230_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


