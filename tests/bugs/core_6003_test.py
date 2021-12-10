#coding:utf-8
#
# id:           bugs.core_6003
# title:        RDB$GET_TRANSACTION_CN works different in Super and Classic
# decription:
#                   Confirmed bug on 4.0.0.2411 CS: got null instead of positive number.
#                   Checked on intermediate build 4.0.0.2416 (08-apr-2021 09:56) - all OK.
#
#                   NB-1: bug can be reproduced using ISQL but it must be lacunhed with '-n' command switch.
#                   NB-2: connection-1 (which finally asks value of rdb$get_transaction_cn(<Tx2>)) must start Tx1
#                         *BEFORE* connection-2 will start his Tx2.
#
# tracker_id:   CORE-6003
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import tpb, Isolation

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
#  import fdb
#  import time
#  import subprocess
#
#  os.environ["ISC_USER"] = 'SYSDBA'
#  os.environ["ISC_PASSWORD"] = 'masterkey'
#  db_conn.close()
#
#  #FB_CLNT=sys.argv[1]
#  DB_NAME = dsn # 'localhost:e40'
#
#  custom_tpb = fdb.TPB()
#  custom_tpb.lock_resolution = fdb.isc_tpb_wait
#  custom_tpb.isolation_level = fdb.isc_tpb_concurrency
#
#  con1 = fdb.connect(dsn=DB_NAME) # , fb_library_name = FB_CLNT )
#  tx1a = con1.trans( default_tpb = custom_tpb )
#  tx1a.begin()
#
#
#  con2 = fdb.connect(dsn=DB_NAME) # , fb_library_name = FB_CLNT )
#  tx2a = con2.trans( default_tpb = custom_tpb )
#  tx2a.begin()
#
#  cur2 = tx2a.cursor()
#  cur2.execute('select current_transaction from rdb$database')
#  for r in cur2:
#      trn2 = int(r[0])
#  tx2a.commit()
#
#  # >>> DO NOT put it here! tx1a must be started BEFORE tx2a! >>> tx1a.begin()
#
#  cur1 = tx1a.cursor()
#  cur1.execute("select 'Result is ' || iif( rdb$get_transaction_cn(%d) is null, 'INCORRECT: NULL.', 'expected: NOT null.') from rdb$database" % trn2)
#  for r in cur1:
#      print(r[0])
#  tx1a.commit()
#
#  #print(con1.firebird_version)
#  cur1.close()
#  cur2.close()
#  con1.close()
#  con2.close()
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    custom_tpb = tpb(isolation=Isolation.CONCURRENCY)
    with act_1.db.connect() as con1:
        tx1a = con1.transaction_manager(custom_tpb)
        tx1a.begin() # tx1a must be started BEFORE tx2a!
        with act_1.db.connect() as con2:
            tx2a = con2.transaction_manager(custom_tpb)
            tx2a.begin()
            #
            cur2 = tx2a.cursor()
            trn2 = cur2.execute('select current_transaction from rdb$database').fetchone()[0]
            tx2a.commit()
            #
            cur1 = tx1a.cursor()
            cur1.execute(f"select 'Result is ' || iif( rdb$get_transaction_cn({trn2}) is null, 'INCORRECT: NULL.', 'expected: NOT null.') from rdb$database")
            assert cur1.fetchone()[0] == 'Result is expected: NOT null.'
