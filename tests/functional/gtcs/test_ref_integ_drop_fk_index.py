#coding:utf-8

"""
ID:          gtcs.ref-integ-drop-fk-index
TITLE:       Index that is used for FK should not be avail for DROP
DESCRIPTION:
    Original test see in:
    https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.4.ISQL.script

    This test uses pre-created script ( <QA_ROOT>/files/gtcs-ref-integ-init.sql ) which creates two
    tables with PK/FK referencing constraint(parent = department, child = employee).
    FK-constraint uses index with name = 'ref_key', and here we try to:
        * DROP this index;
        * insert record in the child table which has no apropriate PK in the parent table.
        (see 'sql_addi' variable which stores SQL statements for that).
    Both actions should fail.

FBTEST: functional.gtcs.ref_integ_drop_fk_index
NOTES:
    [07.08.2024] pzotov
    Splitted expected* text because system triggers now are created in C++/GDML code
    See https://github.com/FirebirdSQL/firebird/pull/8202
    Commit (05-aug-2024 13"45):
    https://github.com/FirebirdSQL/firebird/commit/0cc8de396a3c2bbe13b161ecbfffa8055e7b4929
"""

import pytest
import os
from firebird.qa import *

db = db_factory()

act = python_act('db')

test_expected_stdout = """
    Records affected: 0
"""

expected_stderr_5x = """
    Statement failed, SQLSTATE = 27000
    unsuccessful metadata update
    -DROP INDEX REF_KEY failed
    -action cancelled by trigger (1) to preserve data integrity
    -Cannot delete index used by an Integrity Constraint

    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "REF_KEY" on table "EMPLOYEE"
    -Foreign key reference target does not exist
    -Problematic key value is ("DEPT_NO" = -1)
"""

expected_stderr_6x = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -DROP INDEX REF_KEY failed
    -Cannot delete index used by an Integrity Constraint

    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "REF_KEY" on table "EMPLOYEE"
    -Foreign key reference target does not exist
    -Problematic key value is ("DEPT_NO" = -1)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    
    sql_init = (act.files_dir / 'gtcs-ref-integ-init.sql').read_text()
    sql_addi = '''
        drop index ref_key;
        commit;
        insert into employee( emp_no, last_name, dept_no) values (12, 'e12', -1); -- should FAIL
        set count on;
        select * from employee e where e.dept_no < 0;
    '''
    
    act.expected_stdout = test_expected_stdout
    act.expected_stderr = expected_stderr_5x if act.is_version('<6') else expected_stderr_6x
   
    act.isql(switches=['-q'], input = os.linesep.join( (sql_init, sql_addi) ) )

    assert (act.clean_stdout == act.clean_expected_stdout and
            act.clean_stderr == act.clean_expected_stderr)
