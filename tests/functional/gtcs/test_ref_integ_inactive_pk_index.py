#coding:utf-8

"""
ID:          gtcs.ref_integ_inactive_pk_index
TITLE:       Index that is used for PRIMARY KEY should not be avail for INACTIVE
DESCRIPTION:
  Original test see in:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.7.ISQL.script
FBTEST:      functional.gtcs.ref_integ_inactive_pk_index
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
    violation of PRIMARY or UNIQUE KEY constraint "DEPT_KEY" on table "DEPARTMENT"
    -Problematic key value is ("DEPT_NO" = 1)
"""

test_expected_stdout = """
    Records affected: 1
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    
    sql_init = (act.files_dir / 'gtcs-ref-integ-init.sql').read_text()
    sql_addi = '''
        alter index dept_key inactive;
        commit;
        -- Check that PK index still in use: following must FAIL:
        insert into department( dept_no, dept_name) values (1, 'k1');

        -- Check that it is ALLOWED to insert record into child table (employee)
        -- if value of dept_no exists in the parent table (department)
        -- QUOTE FROM SOURCE TEST:
        -- "... attempts to insert valid records into another table connected
        -- to this table by foreign key constraint. The current behaviour is
        -- that the insertion of valid records fails because of the index being
        -- inactivated in the other connected table (bug 7517)"
        set count on;
        insert into employee values (11, 'e11', 1); -- ==> Records affected: 1
    '''

    act.expected_stdout = test_expected_stdout
    act.expected_stderr = test_expected_stderr
   
    act.isql(switches=['-q'], input = os.linesep.join( (sql_init, sql_addi) ) )

    assert (act.clean_stdout == act.clean_expected_stdout and
            act.clean_stderr == act.clean_expected_stderr)
