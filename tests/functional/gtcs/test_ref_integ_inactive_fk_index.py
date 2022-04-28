#coding:utf-8

"""
ID:          gtcs.ref_integ_inactive_fk_index
TITLE:       Index that is used for FK should not be avail for INACTIVE
DESCRIPTION:
  Original test see in:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.8.ISQL.script
FBTEST:      functional.gtcs.ref_integ_inactive_fk_index
"""
import os
import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

test_expected_stderr = """
    Statement failed, SQLSTATE = 27000
    unsuccessful metadata update
    -ALTER INDEX REF_KEY failed
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
        alter index ref_key inactive; -- should FAIL
        commit;

        insert into employee( emp_no, last_name, dept_no) values (11, 'e11', 1);
        insert into employee( emp_no, last_name, dept_no) values (12, 'e12', -1);

        set count on;
        select * from employee e where e.dept_no < 0;
    '''

    act.expected_stdout = test_expected_stdout
    act.expected_stderr = test_expected_stderr
   
    act.isql(switches=['-q'], input = os.linesep.join( (sql_init, sql_addi) ) )

    assert (act.clean_stdout == act.clean_expected_stdout and
            act.clean_stderr == act.clean_expected_stderr)
