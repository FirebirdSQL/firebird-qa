#coding:utf-8
#
# id:           bugs.core_1073
# title:        SINGULAR buggy when nulls present
# decription:   
# tracker_id:   CORE-1073
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1073

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """create table t (a integer);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# def check(step,cur,statement,exp):
#    cur.execute(statement)
#    r = cur.fetchone()
#    if (exp and (r is None)) or (not exp and (r is not None)):
#      print ('Test FAILED in step ',step,', expectation ',exp)
#      print ('Statement:',statement)
#  
#  c = db_conn.cursor()
#  p_singular = 'select 1 from rdb$database where singular(select * from t where a = 1)'
#  n_singular = 'select 1 from rdb$database where not(singular(select * from t where a = 1))'
#  p_nsingular = 'select 1 from rdb$database where not singular( select * from t where a = 1)'
#  n_nsingular = 'select 1 from rdb$database where not(not singular(select * from t where a = 1))'
#  
#  ins = 'insert into t values (%s)'
#  
#  # Step 1
#  
#  c.execute(ins % '2')
#  c.execute(ins % 'null')
#  db_conn.commit()
#  
#  check(1,c,p_singular,False)
#  check(1,c,n_singular,True)
#  check(1,c,p_nsingular,True)
#  check(1,c,n_nsingular,False)
#  
#  c.execute('delete from t')
#  db_conn.commit()
#  
#  # Step 2
#  
#  c.execute(ins % '1')
#  c.execute(ins % 'null')
#  db_conn.commit()
#  
#  check(2,c,p_singular,True)
#  check(2,c,n_singular,False)
#  check(2,c,p_nsingular,False)
#  check(2,c,n_nsingular,True)
#  
#  c.execute('delete from t')
#  db_conn.commit()
#  
#  # Step 3
#  
#  c.execute(ins % '1')
#  c.execute(ins % 'null')
#  c.execute(ins % '1')
#  db_conn.commit()
#  
#  check(3,c,p_singular,False)
#  check(3,c,n_singular,True)
#  check(3,c,p_nsingular,True)
#  check(3,c,n_nsingular,False)
#  
#  c.execute('delete from t')
#  db_conn.commit()
#  
#  # Step 4
#  
#  c.execute(ins % '1')
#  c.execute(ins % '1')
#  c.execute(ins % 'null')
#  db_conn.commit()
#  
#  check(4,c,p_singular,False)
#  check(4,c,n_singular,True)
#  check(4,c,p_nsingular,True)
#  check(4,c,n_nsingular,False)
#  
#  c.execute('delete from t')
#  db_conn.commit()
#  
#  
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


