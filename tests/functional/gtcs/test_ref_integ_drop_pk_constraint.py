#coding:utf-8

"""
ID:          gtcs.ref_integ_drop_pk_constraint
TITLE:       Constraint of PRIMARY KEY should not be avail for DROP if there is FK that depends on it
DESCRIPTION:
    Original test see in:
    https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/REF_INT.2.ISQL.script
FBTEST:      functional.gtcs.ref_integ_drop_pk_constraint
NOTES:
    [07.08.2024] pzotov
    Splitted expected* text because system triggers now are created in C++/GDML code
    See https://github.com/FirebirdSQL/firebird/pull/8202
    Commit (05-aug-2024 13"45):
    https://github.com/FirebirdSQL/firebird/commit/0cc8de396a3c2bbe13b161ecbfffa8055e7b4929
"""

import os
import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

test_expected_stdout = """
    Records affected: 0
"""

expected_stderr_5x = """
    Statement failed, SQLSTATE = 27000
    unsuccessful metadata update
    -DROP INDEX DEPT_KEY failed
    -action cancelled by trigger (1) to preserve data integrity
    -Cannot delete index used by an Integrity Constraint

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "DEPT_KEY" on table "DEPARTMENT"
    -Problematic key value is ("DEPT_NO" = 1)
"""

expected_stderr_6x = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -DROP INDEX DEPT_KEY failed
    -Cannot delete index used by an Integrity Constraint

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "DEPT_KEY" on table "DEPARTMENT"
    -Problematic key value is ("DEPT_NO" = 1)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    
    sql_init = (act.files_dir / 'gtcs-ref-integ-init.sql').read_text()
    sql_addi = '''
        drop index dept_key;
        -- Check that PK index still in use: following must FAIL:
        set count on;
        insert into department( dept_no, dept_name) values (1, 'k1');
    '''

    act.expected_stdout = test_expected_stdout
    act.expected_stderr = expected_stderr_5x if act.is_version('<6') else expected_stderr_6x
   
    act.isql(switches=['-q'], input = os.linesep.join( (sql_init, sql_addi) ) )

    assert (act.clean_stdout == act.clean_expected_stdout and
            act.clean_stderr == act.clean_expected_stderr)
