#coding:utf-8

"""
ID:          gtcs.ref_integ_inactive_pk_index
TITLE:       Index that is used for PRIMARY KEY should not be avail for INACTIVE
DESCRIPTION:
  Original test see in:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.7.ISQL.script
FBTEST:      functional.gtcs.ref_integ_inactive_pk_index
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stderr = """
    Statement failed, SQLSTATE = 27000
    unsuccessful metadata update
    -ALTER INDEX DEPT_KEY failed
    -action cancelled by trigger (2) to preserve data integrity
    -Cannot deactivate index used by an integrity constraint

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "DEPT_KEY" on table "DEPARTMENT"
    -Problematic key value is ("DEPT_NO" = '1')
"""

expected_stdout = """
    Records affected: 1
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
#      alter index dept_key inactive;
#      commit;
#      -- Check that PK index still in use: following must FAIL:
#      insert into department( dept_no, dept_name) values (1, 'k1');
#
#      -- Check that it is ALLOWED to insert record into child table (employee)
#      -- if value of dept_no exists in the parent table (department)
#      -- QUOTE FROM SOURCE TEST:
#      -- "... attempts to insert valid records into another table connected
#      -- to this table by foreign key constraint. The current behaviour is
#      -- that the insertion of valid records fails because of the index being
#      -- inactivated in the other connected table (bug 7517)"
#      set count on;
#      insert into employee values (11, 'e11', 1); -- ==> Records affected: 1
#  '''
#
#  runProgram('isql', [ dsn], os.linesep.join( (sql_init, sql_addi) ) )
#---
