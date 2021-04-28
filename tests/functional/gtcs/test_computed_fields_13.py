#coding:utf-8
#
# id:           functional.gtcs.computed_fields_13
# title:        computed-fields-13
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_13.script
#               	SQL script for creating test database ('gtcs_sp1.fbk') and fill it with some data:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROCS_QA_INIT_ISQL.script
#                   Checked on: 4.0.0.1803 SS; 3.0.6.33265 SS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    point-1 10 30
    point-2 11 44 220
  """
expected_stderr_1 = """
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

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

