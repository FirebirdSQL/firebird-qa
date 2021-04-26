#coding:utf-8
#
# id:           bugs.core_1112
# title:        Crash when dealing with a string literal longer than 32K
# decription:   This test may crash the server
# tracker_id:   CORE-1112
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1112

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  longstr = 'abc' * 10930
#  try:
#    c.execute("select * from rdb$database where '%s' = 'a'" % longstr)
#  except:
#    pass
#  
#  try:
#    c.execute("select * from rdb$database where '%s' containing 'a'" % longstr)
#  except:
#    pass
#  c.execute("select 'a' from rdb$database")
#  print (c.fetchall())
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """[('a',)]
"""

@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_core_1112_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


