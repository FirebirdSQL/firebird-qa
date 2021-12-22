#coding:utf-8
#
# id:           functional.session.alter_session_reset_allow_2pc_prepared
# title:        
#                   ALTER SESSION RESET: do NOT raise error if prepared 2PC transactions present.
#                
# decription:   
#                  Test issue from CORE-5832 about ALTER SESSION RESET:
#                  "throw error (isc_ses_reset_err) if any open transaction exist in current conneciton,
#                   except of ... prepared 2PC transactions which is allowed and ignored by this check"
#               
#                  We create two databases with table (id int, x int) in each of them.
#                  Then we create two connections (one per each DB).
#               
#                  These connections are added to the instance of fdb.ConnectionGroup() in order to have
#                  ability to use 2PC mechanism.
#               
#                  In the first connection we start TWO transactions, in the second it is enough to start one.
#                  Then we do trivial DML in each of these three transactions: insert one row in a table.
#               
#                  Finally, we run prepare() method in one of pair transactions that belong to 1st connection.
#                  After this, we must be able to run ALTER SESSION RESET in the *second* Tx of this pair, and
#                  this statement must NOT raise any error.
#               
#                  NB! Without prepare() such action must lead to exception:
#                  "SQLCODE: -901 / Cannot reset user session / There are open transactions (2 active)"
#               
#                  Output of this test must remain EMPTY.
#                  
#                  Checked on 4.0.0.2307 SS/CS.
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import time
#  import subprocess
#  import re
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  
#  #--------------------------------------------
#  
#  db_conn.close()
#  svc = services.connect(host='localhost', user=user_name, password=user_password)
#  fb_home = svc.get_home_directory()
#  
#  
#  DBNAME_A = os.path.join(context['temp_directory'],'tmp_2pc_a.fdb')
#  DBNAME_B = os.path.join(context['temp_directory'],'tmp_2pc_b.fdb')
#  
#  if os.path.isfile(DBNAME_A):
#      os.remove(DBNAME_A)
#  if os.path.isfile(DBNAME_B):
#      os.remove(DBNAME_B)
#  
#  con1 = fdb.create_database( dsn = 'localhost:' + DBNAME_A)
#  con2 = fdb.create_database( dsn = 'localhost:' + DBNAME_B)
#  
#  con1.execute_immediate( 'create table test(id int, x int, constraint test_pk primary key(id) using index test_pk)' )
#  con1.commit()
#  
#  con2.execute_immediate( 'create table test(id int, x int, constraint test_pk primary key(id) using index test_pk)' )
#  con2.commit()
#  
#  con1.close()
#  con2.close()
#  
#  cgr = fdb.ConnectionGroup()
#  
#  con1 = fdb.connect( dsn = 'localhost:' + DBNAME_A)
#  con2 = fdb.connect( dsn = 'localhost:' + DBNAME_B)
#  
#  cgr.add(con1)
#  cgr.add(con2)
#   
#  # https://pythonhosted.org/fdb/reference.html#fdb.TPB
#  # https://pythonhosted.org/fdb/reference.html#fdb.Connection.trans
#  
#  tx1a = con1.trans()
#  tx2 = con2.trans()
#  
#  tx1b = con1.trans()
#  
#  tx1a.begin()
#  tx2.begin()
#  tx1b.begin()
#  
#  cur1a=tx1a.cursor()
#  cur2=tx2.cursor()
#  cur1b=tx1b.cursor()
#  
#  cur1a.execute( "insert into test(id, x) values( ?, ? )", (1, 111) )
#  cur2.execute( "insert into test(id, x) values( ?, ? )", (2, 222) )
#  cur1b.execute( "insert into test(id, x) values( ?, ? )", (3, 333) )
#  
#  # ::: NB ::: WITHOUT following prepare() exception will raise:
#  # Error while executing SQL statement: / SQLCODE: -901 / Cannot reset user session / There are open transactions (2 active); -901; 335545206L
#  tx1a.prepare()
#  
#  cur1b.execute( "alter session reset" )
#  
#  cur1a.close()
#  cur1b.close()
#  cur2.close()
#  tx1a.rollback()
#  tx1b.rollback()
#  tx2.rollback()
#  
#  # ::: NB :::
#  # We can NOT ecplicitly close connections that participate in ConnectionGroup.
#  # Exception will raise in that case: "Cannot close a connection that is a member of a ConnectionGroup."
#  #con1.close()
#  #con2.close()
#  
#  cgr.clear()
#  
#  # change state of test databases to full shutdown otherwise get "Object in use" (set linger = 0 does not help!)
#  runProgram('gfix',['localhost:' + DBNAME_A,'-shut','full','-force','0'])
#  runProgram('gfix',['localhost:' + DBNAME_B,'-shut','full','-force','0'])
#  
#  cleanup( (DBNAME_A, DBNAME_B) )
#  
#---
act_1 = python_act('db_1', substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


