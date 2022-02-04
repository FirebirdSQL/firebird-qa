#coding:utf-8

"""
ID:          computed-fields-13
FBTEST:      functional.gtcs.computed_fields_13
TITLE:       Computed fields
DESCRIPTION:
  Original test see in:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_13.script
  SQL script for creating test database ('gtcs_sp1.fbk') and fill it with some data:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROCS_QA_INIT_ISQL.script

  Check that it is not allowed to drop column which is referenced by computed-by column.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set heading off;
    /*---------------------------------------------*/
    /* Create a table with computed field.         */
    /*---------------------------------------------*/
    create table t0 (a integer, af computed by (a*3));
    insert into t0(a) values(10);

    /*---------------------------------------------*/
    /* Create a table with nested computed field.  */
    /*---------------------------------------------*/
    create table t1 (a integer, af computed by (a*4), afaf computed by (af*5));
    insert into t1(a) values(11);

    commit;

    /*---------------------------------------------------------------------*/
    /* Now alter table and drop the field which is used in computed field. */
    /* It shouldn't allow you to drop the field.                           */
    /*---------------------------------------------------------------------*/
    alter table t0 drop a;
    select 'point-1' msg, p.* from t0 p;

    /*---------------------------------------------------------------------*/
    /* Now alter table and drop the computed field which is used in other  */
    /* computed field.                                                     */
    /* It shouldn't allow you to drop the field.                           */
    /*---------------------------------------------------------------------*/
    alter table t1 drop af;
    select 'point-2' msg, p.* from t1 p;
"""

act = isql_act('db', test_script, substitutions=[('=', ''), ('[ \t]+', ' ')])

expected_stdout = """
    point-1 10 30
    point-2 11 44 220
"""

expected_stderr = """
    Statement failed, SQLSTATE 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN T0.A
    -there are 1 dependencies
    Statement failed, SQLSTATE 42000

    unsuccessful metadata update
    -cannot delete
    -COLUMN T1.AF
    -there are 1 dependencies
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
