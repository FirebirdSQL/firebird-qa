#coding:utf-8

"""
ID:          gtcs.ref_integ_inactive_pk_index_2
TITLE:       Index that is used for PRIMARY KEY should not be avail for INACTIVE
DESCRIPTION:
  Original test see in:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.7.ISQL.script

  NOTE on difference from GTCS/tests/REF_INT.7.ISQL:
  we attampt to insert into child table (employee) record which VIOLATES ref. integrity.
  See quote from source test:
    attempts to insert records into another table in violation of the referential
    integrity constraint. The current behaviour is that even though the
    unique index has been inactivated, the insertion fails because of referential
    integrity violation.. (bug 7517)
FBTEST:      functional.gtcs.ref_integ_inactive_pk_index_2
"""

import os
import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

test_expected_stderr = """
    Statement failed, SQLSTATE = 27000
    unsuccessful metadata update
    -ALTER INDEX DEPT_KEY failed
    -action cancelled by trigger (2) to preserve data integrity
    -Cannot deactivate index used by an integrity constraint

    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "REF_KEY" on table "EMPLOYEE"
    -Foreign key reference target does not exist
    -Problematic key value is ("DEPT_NO" = -1)
"""

test_expected_stdout = """
    Records affected: 0
"""


@pytest.mark.version('>=3.0')
def test_1(act: Action):
    
    sql_init = (act.files_dir / 'gtcs-ref-integ-init.sql').read_text()
    sql_addi = '''
        alter index dept_key inactive;
        commit;
        set count on;
        insert into employee values (11, 'e11', -1); -- ==> Records affected: 0
    '''

    act.expected_stdout = test_expected_stdout
    act.expected_stderr = test_expected_stderr
   
    act.isql(switches=['-q'], input = os.linesep.join( (sql_init, sql_addi) ) )

    assert (act.clean_stdout == act.clean_expected_stdout and
            act.clean_stderr == act.clean_expected_stderr)

