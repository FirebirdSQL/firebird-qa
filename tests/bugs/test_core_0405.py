#coding:utf-8
#
# id:           bugs.core_0405
# title:        Garbage vs indices/constraints
# decription:   
#                   Confirmed bug on 3.0.4.32924, got:
#                       DatabaseError:
#                       Error while commiting transaction:
#                       - SQLCODE: -803
#                       - attempt to store duplicate value (visible to active transactions) in unique index "TEST_X"
#                       -803
#                       335544349
#                       ----------------------------------------------------
#                   :: NB ::
#                   No error on Firebird 4.0 (any: SS,SC, CS).
#                   Works OK on: 4.0.0.838
#                 
# tracker_id:   CORE-0405
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import fdb
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  con=fdb.connect( dsn=dsn, no_gc=1 )
#  #print( con.firebird_version )
#  
#  con.execute_immediate('recreate table test(x int)')
#  con.commit()
#  cur=con.cursor()
#  
#  stm='insert into test( x ) values( ? )'
#  val = [ (2,), (3,), (3,), (2,) ]
#  cur.executemany(  stm, val )
#  
#  cur.execute('select x from test order by x')
#  for r in cur:
#      print(r[0])
#  
#  cur.execute('delete from test')
#  
#  cur.execute('select count(*) from test')
#  for r in cur:
#      print(r[0])
#  
#  con.execute_immediate('create unique index test_x on test(x)')
#  con.commit()
#  
#  
#  cur.execute("select rdb$index_name from rdb$indices where rdb$relation_name='TEST'")
#  for r in cur:
#      print( r[0].rstrip()  )
#  
#  con.close()
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    2
    2
    3
    3
    0
    TEST_X
  """

@pytest.mark.version('>=3.0.4')
@pytest.mark.xfail
def test_core_0405_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


