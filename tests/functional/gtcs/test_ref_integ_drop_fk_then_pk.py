#coding:utf-8

"""
ID:          gtcs.ref-integ-drop-fk-then-pk
TITLE:       Outcome must be SUCCESS if first we drop FK and after this PK constraint
DESCRIPTION:
  Original test see in:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.1.ISQL.script
FBTEST:      functional.gtcs.ref_integ_drop_fk_then_pk
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    Records affected: 1
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
