#coding:utf-8
#
# id:           bugs.core_0210
# title:        CS server crash altering SP in 2 connect
# decription:
#
# tracker_id:   CORE-0210
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import tpb, Isolation

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

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
#  stm1='''create or alter procedure sp_test as
#  begin
#      exit;
#  end
#  '''
#  stm2='''create or alter procedure sp_test as
#      declare x int;
#  begin
#      exit;
#  end
#  '''
#
#  con1 = fdb.connect(dsn=dsn)
#  con2 = fdb.connect(dsn=dsn)
#
#  xtpb = ( [ fdb.isc_tpb_concurrency  ] )
#
#  con1.begin( tpb = xtpb )
#
#  cur1=con1.cursor()
#  cur2=con2.cursor()
#
#  cur1.execute(stm1)
#  con1.commit()
#
#  con2.begin( tpb = xtpb )
#  cur2.execute(stm2)
#  con2.commit()
#
#  con1.begin( tpb = xtpb )
#  cur1.execute(stm1)
#  con1.commit()
#
#  con1.close()
#  con2.close()
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    stm1 = '''create or alter procedure sp_test as
    begin
        exit;
    end
    '''
    stm2 = '''create or alter procedure sp_test as
        declare x int;
    begin
        exit;
    end
    '''
    custom_tpb = tpb(isolation=Isolation.CONCURRENCY)
    with act_1.db.connect() as con1, act_1.db.connect() as con2:
        con1.begin(custom_tpb)
        cur1 = con1.cursor()
        cur2 = con2.cursor()

        cur1.execute(stm1)
        con1.commit()

        con2.begin(custom_tpb)
        cur2.execute(stm2)
        con2.commit()

        con1.begin(custom_tpb)
        cur1.execute(stm1)
        con1.commit()


