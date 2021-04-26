#coding:utf-8
#
# id:           bugs.core_6382
# title:        FK-trigger accessing a table prevents concurrent DDL command from dropping that table
# decription:   
#                   Test creates two tables which are linked by master-detail relationship.
#                   We add one record into the main table and then update it with issuing further COMMIT.
#                   After this we try to DROP this table in another connect.
#               
#                   If this connect started WAIT transaction (i.e. without lock timeout) then it can hang forever if case of
#                   regression of this fix. Because of this, we change its waiting mode by adding lock_timeout parameter to 
#                   TPB and set it to 1 second.
#               
#                   BEFORE fix this lead to:
#                       DatabaseError: / Error while commiting transaction: / - SQLCODE: -901
#                       - lock time-out on wait transaction / - unsuccessful metadata update
#                       - object TABLE "T_DETL" is in use / -901 / 335544510
#               
#                  AFTER fix this DROP TABLE statement must pass without any error.
#               
#                  Checked on 4.0.0.2141.
#                
# tracker_id:   CORE-6382
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t_detl(id int primary key using index t_detl_pk, pid int);
    recreate table t_main(id int primary key using index t_main_pk);
    alter table t_detl add constraint t_detl_fk foreign key(pid) references t_main(id) on update cascade using index t_detl_fk;
    commit;
    insert into t_main values(123);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import fdb
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  custom_tpb = fdb.TPB()
#  custom_tpb.lock_resolution = fdb.isc_tpb_wait
#  
#  # NB: adding this timeout does NOT change WAIT-nature of transaction as it is considered by engine.
#  # (in other words: such transaction will not became 'no wait' which must not be used in this test):
#  custom_tpb.lock_timeout = 1
#  
#  con1 = fdb.connect( dsn = dsn, isolation_level = custom_tpb)
#  con2 = fdb.connect( dsn = dsn, isolation_level = custom_tpb)
#  
#  con1.execute_immediate('update t_main set id=-id')
#  con1.commit()
#  
#  con2.execute_immediate('drop table t_detl')
#  con2.commit()
#  
#  cur=con2.cursor()
#  cur.execute( "select r.rdb$relation_name from rdb$database d left join rdb$relations r on r.rdb$relation_name = upper('t_detl')" )
#  for r in cur:
#      print(r[0])
#  cur.close()
#  con2.close()
#  con1.close()
#  
#  print('Passed.')
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    None
    Passed.
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_core_6382_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


