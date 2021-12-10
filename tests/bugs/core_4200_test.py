#coding:utf-8
#
# id:           bugs.core_4200
# title:        An uncommitted select of the pseudo table sec$users blocks new database connections
# decription:
#                   Checked on: 4.0.0.1635: OK, 1.866s; 3.0.5.33180: OK, 1.869s.
#
#               [pcisar] 18.11.2021
#               New test implementation according to bug description:
#               session 1:
#                  connect to test database
#                  start transaction
#                  select * from sec$users
#                  (do *not* commit)
#               session 2:
#                  connect to test database => results in sql error -902;
#                  engine code 335544472 Your user name and password are not defined.
#                  Ask your database administrator to set up a Firebird login.
#
# tracker_id:   CORE-4200
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import tpb, Isolation

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  db_conn.close()
#
#  custom_tpb = fdb.TPB()
#  custom_tpb.access_mode = fdb.isc_tpb_read
#  custom_tpb.isolation_level = (fdb.isc_tpb_read_committed, fdb.isc_tpb_rec_version)
#  custom_tpb.lock_resolution = fdb.isc_tpb_nowait
#
#  con1=fdb.connect(dsn = dsn, user = 'SYSDBA', password = 'masterkey')
#  trn1=con1.trans( default_tpb = custom_tpb )
#  cur1=trn1.cursor()
#  cur1.execute('select sec$user_name from sec$users')
#  for r in cur1:
#      pass
#
#  #custom_con = fdb.Connection()
#  #custom_con._default_tpb = custom_tpb
#
#  con2=fdb.connect( dsn = dsn, user = 'tmp$c4200_leg', password = '123') #, connection_class = custom_con)
#  con3=fdb.connect( dsn = dsn, user = 'tmp$c4200_srp', password = '123') #, connection_class = custom_con)
#
#  check_sql='select mon$user as who_am_i, mon$auth_method as auth_method from mon$attachments'
#
#  trn2=con2.trans( default_tpb = custom_tpb )
#  cur2=trn2.cursor()
#  cur2.execute(check_sql)
#
#  trn3=con3.trans( default_tpb = custom_tpb )
#  cur3=trn3.cursor()
#  cur3.execute(check_sql)
#
#  for c in (cur2, cur3):
#      cur_cols=c.description
#      for r in c:
#          for i in range(0,len(cur_cols)):
#              print( cur_cols[i][0],':', r[i] )
#      c.close()
#
#  trn2.rollback()
#  trn3.rollback()
#
#  con2.close()
#  con3.close()
#
#  cur1.close()
#  con1.execute_immediate('drop user tmp$c4200_leg using plugin Legacy_UserManager')
#  con1.execute_immediate('drop user tmp$c4200_srp using plugin Srp')
#  con1.commit()
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    custom_tpb = tpb(isolation=Isolation.READ_COMMITTED_RECORD_VERSION, lock_timeout=0)
    #
    with act_1.db.connect() as con1:
        trn1 = con1.transaction_manager(custom_tpb)
        cur1 = trn1.cursor()
        cur1.execute('select sec$user_name from sec$users')
        with act_1.db.connect() as con2:
            pass # Connect should not raise an exception
