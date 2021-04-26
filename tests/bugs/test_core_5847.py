#coding:utf-8
#
# id:           bugs.core_5847
# title:        "Malformed string" instead of key value in PK violation error message
# decription:   
#                    Confirmed bug on: 3.0.4.32972, 4.0.0.955.
#                    Works fine on:
#                       FB25SC, build 2.5.9.27112: OK, 1.187s.
#                       FB30SS, build 3.0.4.32992: OK, 1.485s.
#                       FB40SS, build 4.0.0.1023: OK, 1.500s.
#                
# tracker_id:   CORE-5847
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = [('Problematic key value is .*', 'Problematic key value is')]

init_script_1 = """
    recreate table test(
        uid char(16) character set octets, 
        constraint test_uid_pk primary key(uid) using index test_uid_pk 
    );
    commit;
    insert into test values( gen_uuid() );
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#  
#  con1 = fdb.connect(dsn = dsn, charset = 'utf8')
#  con2 = fdb.connect(dsn = dsn)
#  
#  sql_cmd='insert into test(uid) select uid from test rows 1'
#  cur1=con1.cursor()
#  cur2=con2.cursor()
#  for i in(1,2,):
#      c = cur1 if i==1 else cur2
#      try:
#          c.execute(sql_cmd)
#      except Exception, e:
#          for k,x in enumerate(e):
#              print(i,' ',k,':',x)
#      i+=1
#  
#  con1.close()
#  con2.close()
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1   0 : Error while executing SQL statement:
    - SQLCODE: -803
    - violation of PRIMARY or UNIQUE KEY constraint "TEST_UID_PK" on table "TEST"
    - Problematic key value is ("UID" = x'AA70F788EB634073AD328C284F775A3E')
    1   1 : -803
    1   2 : 335544665

    2   0 : Error while executing SQL statement:
    - SQLCODE: -803
    - violation of PRIMARY or UNIQUE KEY constraint "TEST_UID_PK" on table "TEST"
    - Problematic key value is ("UID" = x'AA70F788EB634073AD328C284F775A3E')
    2   1 : -803
    2   2 : 335544665
  """

@pytest.mark.version('>=2.5.9')
@pytest.mark.xfail
def test_core_5847_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


