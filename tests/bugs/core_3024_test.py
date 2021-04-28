#coding:utf-8
#
# id:           bugs.core_3024
# title:        Error "no current record for fetch operation" after ALTER VIEW
# decription:   
#                  Confirmed error on: WI-V2.5.6.26962 (SC), fixed on: WI-V2.5.6.26963.
#                  Checked on WI-V3.0.0.32268 (SS, SC, CS).
#                  Checked on fdb version 1.5.
#                
# tracker_id:   CORE-3024
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = [('-', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# db_conn.close()
#  
#  att1=kdb.connect(dsn=dsn.encode(),user='SYSDBA',password='masterkey')
#  att2=kdb.connect(dsn=dsn.encode(),user='SYSDBA',password='masterkey')
#  
#  trn1=att1.trans()
#  
#  cur1=trn1.cursor()
#  
#  cur1.execute("create table t(a int, b int, c int)")   # att_12, tra_4
#  cur1.execute("create view v as select a,b from t")
#  trn1.commit()
#  
#  cur1.execute("insert into t values(1,2,3)")           # att_12, tra_5
#  cur1.execute("select * from v")
#  trn1.commit()
#  
#  trn2=att2.trans()
#  cur2=trn2.cursor()
#  cur2.execute("select * from v")                       # att_13, tra_7
#  trn2.commit()
#  
#  cur1.execute("alter view v as select a, b, c from t") # att-12, tra_8
#  trn1.commit()
#  
#  cur2.execute("select * from v")                       # att_13, tra_9
#  printData(cur2)
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A           B           C
    1           2           3
  """

@pytest.mark.version('>=2.5.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


