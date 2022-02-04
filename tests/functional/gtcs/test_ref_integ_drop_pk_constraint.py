#coding:utf-8

"""
ID:          gtcs.ref_integ_drop_pk_constraint
TITLE:       Constraint of PRIMARY KEY should not be avail for DROP if there is FK that depends on it
DESCRIPTION:
  Original test see in:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.2.ISQL.script
FBTEST:      functional.gtcs.ref_integ_drop_pk_constraint
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stderr = """
    Statement failed, SQLSTATE = 27000
    unsuccessful metadata update
    -DROP INDEX DEPT_KEY failed
    -action cancelled by trigger (1) to preserve data integrity
    -Cannot delete index used by an Integrity Constraint

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "DEPT_KEY" on table "DEPARTMENT"
    -Problematic key value is ("DEPT_NO" = '1')
"""

expected_stdout = """
    Records affected: 0
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3.0')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

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
#      drop index dept_key;
#      -- Check that PK index still in use: following must FAIL:
#      set count on;
#      insert into department( dept_no, dept_name) values (1, 'k1');
#  '''
#
#  runProgram('isql', [ dsn], os.linesep.join( (sql_init, sql_addi) ) )
#---
