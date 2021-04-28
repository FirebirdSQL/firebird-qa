#coding:utf-8
#
# id:           bugs.core_5949
# title:        Bugcheck could happen when read-only database with non-zero linger is set to read-write mode
# decription:   
#                   Confirmed bug on 3.0.4.33053, got message in firebird.log:
#                   ===
#               	Database: ...\\FPT-REPO\\TMP\\BUGS.CORE_5949.FDB
#               	internal Firebird consistency check (next transaction older than oldest active transaction (266), file: cch.cpp line: 4830)
#                   ===	
#                   Checked on 3.0.5.33084, 4.0.0.1249, 4.0.0.1340 -- works fine.
#                 
# tracker_id:   CORE-5949
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import fdb
#  from fdb import services as fbsvc
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  DB_NAME = '$(DATABASE_LOCATION)' + 'bugs.core_5949.fdb'
#  
#  def change_db_access_mode( a_host, a_db_name, a_required_access ):
#      global fbsvc
#      svc=fbsvc.connect( host = a_host )
#      svc.set_access_mode( a_db_name, a_required_access) # services.ACCESS_READ_WRITE or services.ACCESS_READ_ONLY
#      svc.close()
#      return None
#  #------------------------------------
#  
#  db_conn.execute_immediate('alter database set linger to 60')
#  db_conn.commit()
#  db_conn.close()
#  
#  #------------------------------------
#  
#  change_db_access_mode( 'localhost', DB_NAME, fbsvc.ACCESS_READ_ONLY )
#  
#  con=fdb.connect(dsn = dsn)
#  cur=con.cursor()
#  cur.execute('select r.rdb$linger, d.mon$read_only from rdb$database r cross join mon$database d')
#  for r in cur:
#      print(r[0],r[1])
#  con.commit()
#  con.close()
#  
#  #------------------------------------
#  change_db_access_mode( 'localhost', DB_NAME, fbsvc.ACCESS_READ_WRITE )
#  
#  print('COMPLETED.')
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    60 1
    COMPLETED.
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


