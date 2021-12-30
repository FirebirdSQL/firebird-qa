#coding:utf-8
#
# id:           functional.gtcs.ref_integ_drop_fk_then_pk
# title:        GTCS/tests/REF_INT.1.ISQL ; ref-integ-drop-fk-then-pk. Outcome must be SUCCESS if first we drop FK and after this PK constraint.
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.1.ISQL.script
#                   Checked on: 4.0.0.1806 SS; 3.0.6.33272 CS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import subprocess
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  with open( os.path.join(context['files_location'],'gtcs-ref-integ.sql'), 'r') as f:
#      sql_init = f.read()
#  
#  sql_addi='''
#      alter table employee drop constraint ref_key;
#      alter table department drop constraint dept_key;
#      set count on;
#      -- Folowing two statements should PASS:
#      insert into department( dept_no, dept_name) values (1, 'k1');
#      insert into employee( emp_no, last_name, dept_no) values (12, 'e12', -1); -- should FAIL
#  '''
#  
#  runProgram('isql', [ dsn], os.linesep.join( (sql_init, sql_addi) ) )
#---
act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 1
    Records affected: 1
"""

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


