#coding:utf-8
#
# id:           bugs.core_5062
# title:        CHAR_TO_UUID on column with index throws expression evaluation not supported Human readable UUID argument for CHAR_TO_UUID must be of exact length 36
# decription:   
# tracker_id:   CORE-5062
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  # ::: NB ::: Could not reproduce ticket issue on x86.
#  # Checked on: WI-V2.5.4.26856,  WI-V3.0.0.31948 (Python = 2.7 x86, fdb = 1.5).
#  
#  import fdb
#  db_conn.close()
#  
#  sql_ddl='''recreate table test_uuid(
#      datavalue int, 
#      uuid char(16) character set octets, 
#      constraint test_uuid_unq unique(uuid)
#  );
#  commit;
#  insert into test_uuid(datavalue, uuid) values( 1, char_to_uuid('57F2B8C7-E1D8-4B61-9086-C66D1794F2D9') );
#  --insert into test_uuid(datavalue, uuid) values( 2, char_to_uuid('37F2B8C3-E1D8-4B31-9083-C33D1794F2D3') );
#  commit;
#  '''
#  
#  runProgram('isql',['-user',user_name, '-pas',user_password, dsn],sql_ddl)
#  
#  con2 = fdb.connect(dsn=dsn, user=user_name, password=user_password, charset='utf8')
#  
#  xcur2 = con2.cursor()
#  psSel = xcur2.prep("select datavalue from test_uuid where uuid = char_to_uuid(?)")
#  
#  print ( psSel.plan )
#  xcur2.execute(psSel, [('57F2B8C7-E1D8-4B61-9086-C66D1794F2D9')])
#  for row in xcur2:
#    print( row[0] )
#  
#  con2.close()
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST_UUID INDEX (TEST_UUID_UNQ))
    1
  """

@pytest.mark.version('>=2.5.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


