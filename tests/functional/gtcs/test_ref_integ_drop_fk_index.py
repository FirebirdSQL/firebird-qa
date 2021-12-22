#coding:utf-8
#
# id:           functional.gtcs.ref_integ_drop_fk_index
# title:        GTCS/tests/REF_INT.4.ISQL ; ref-integ-drop-fk-index. Index that is used for FK should not be avail for DROP.
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.4.ISQL.script
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
#      drop index ref_key;
#      commit;
#      insert into employee( emp_no, last_name, dept_no) values (12, 'e12', -1); -- should FAIL
#      set count on;
#      select * from employee e where e.dept_no < 0;
#  '''
#  
#  runProgram('isql', [ dsn], os.linesep.join( (sql_init, sql_addi) ) )
#---
act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 27000
    unsuccessful metadata update
    -DROP INDEX REF_KEY failed
    -action cancelled by trigger (1) to preserve data integrity
    -Cannot delete index used by an Integrity Constraint

    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "REF_KEY" on table "EMPLOYEE"
    -Foreign key reference target does not exist
    -Problematic key value is ("DEPT_NO" = '-1')
"""

expected_stdout_1 = """
    Records affected: 0
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


