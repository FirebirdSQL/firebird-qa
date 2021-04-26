#coding:utf-8
#
# id:           bugs.core_6529
# title:        Error "no current record for fetch operation" when sorting by a international string
# decription:   
#                   Confirmed bug on 4.0.0.2394, got:
#                       - SQLCODE: -508 / - no current record for fetch operation / -508 / 335544348
#                   Checked on 4.0.0.2401 - all OK.
#                
# tracker_id:   CORE-6529
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  db_conn.execute_immediate('recreate table t (f varchar(32765) character set win1251)')
#  db_conn.commit()
#  
#  cur = db_conn.cursor()
#  
#  cur.execute( "insert into t(f) values(?)", ('W' * 1000,) )
#  # no commit here!
#  
#  try:
#      cur.execute('select f from t order by 1')
#      for r in cur:
#          pass
#      print('Passed.')
#  except Exception,e:
#      print('Exception in cursor:')
#      print( '-' * 30 )
#      for x in e:
#          print(x)
#      print( '-' * 30 )
#  finally:
#      cur.close()
#      db_conn.close()
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Passed.
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_core_6529_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


