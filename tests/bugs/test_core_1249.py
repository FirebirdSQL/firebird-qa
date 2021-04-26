#coding:utf-8
#
# id:           bugs.core_1249
# title:        Full shutdown mode doesn't work on Classic if there are other connections to the database
# decription:   This bug affects only Windows CS, but we'll test all platforms and architectures anyway.
# tracker_id:   CORE-1249
# min_versions: []
# versions:     2.0.2
# qmid:         bugs.core_1249

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  cur1 = db_conn.cursor()
#  #cur1.execute('select 1 from rdb$database')
#  runProgram('gfix',[dsn,'-user',user_name,'-pas',user_password,'-shut','full','-force','0'])
#  
#  try:
#      cur1.execute('select 1 from rdb$database')
#      print ('BUG! Operation allowed after shutdown!')
#  except Exception, e:
#      print("OK: operation not allowed.")
#      print( ' '.join( ( 'Exception', ('DOES' if 'shutdown' in e[0] else 'does NOT'), 'contain text about shutdown.') ) )
#      if 'shutdown' not in e[0]:
#          print(e[0])
#  
#  #    Error while starting transaction:
#  #    - SQLCODE: -902
#  #    - connection shutdown
#  #    - Database is shutdown. <<<<<<<<<<<<<<<<<<<< NEW message in 4.0
#  #
#  # Following messages can appear now after 'connection shutdown' (letter from dimitr, 08-may-2017 20:41):
#  #   isc_att_shut_killed: Killed by database administrator
#  #   isc_att_shut_idle: Idle timeout expired
#  #   isc_att_shut_db_down: Database is shutdown
#  #   isc_att_shut_engine: Engine is shutdown
#  
#  runProgram('gfix',[dsn,'-user',user_name,'-pas',user_password,'-online'])
#  
#  # 'substitutions': [('^.*shutdown','shutdown')]
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    OK: operation not allowed.
    Exception DOES contain text about shutdown.
  """

@pytest.mark.version('>=2.0.2')
@pytest.mark.xfail
def test_core_1249_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


