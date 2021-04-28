#coding:utf-8
#
# id:           bugs.core_5837
# title:        Inconsistent results when working with GLOBAL TEMPORARY TABLE ON COMMIT PRESERVE ROWS
# decription:   
#                   Samples were provided by Vlad, privately.
#                   Confirmed bug on 3.0.4.32972, 4.0.0.955; SUPERSERVER only (see also note in the ticket)
#                   Works fine on:
#                       3.0.4.32985, 4.0.0.1000
#                
# tracker_id:   CORE-5837
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate global temporary table gtt(id int) on commit preserve rows;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import subprocess
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  con1=fdb.connect( dsn = dsn )
#  con2=fdb.connect( dsn = dsn )
#  
#  cur2=con2.cursor()
#  
#  # Following 'select count' is MANDATORY for reproduce:
#  #######################################
#  cur2.execute('select count(*) from gtt');
#  for r in cur2:
#      pass 
#  
#  cur1=con1.cursor()
#  cur1.execute('insert into gtt(id) values( ? )', (1,) )
#  cur1.execute('insert into gtt(id) values( ? )', (1,) )
#  
#  cur2.execute('insert into gtt(id) values( ? )', (2,) )
#  
#  con1.rollback()
#  
#  
#  cur2.execute('insert into gtt(id) select 2 from rdb$types rows 200', (2,) )
#  con2.commit()
#  
#  cur1.execute('insert into gtt(id) values( ? )', (11,) )
#  cur1.execute('insert into gtt(id) values( ? )', (11,) )
#  
#  print('con1.rollback: point before.')
#  con1.rollback()
#  print('con1.rollback: point after.')
#  
#  
#  con1.close()
#  con2.close()
#  print('sample-2 finished OK.')
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    con1.rollback: point before.
    con1.rollback: point after.
    sample-2 finished OK.
  """

@pytest.mark.version('>=3.0.3')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


