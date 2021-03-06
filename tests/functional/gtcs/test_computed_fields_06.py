#coding:utf-8
#
# id:           functional.gtcs.computed_fields_06
# title:        computed-fields-06
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_06.script
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

    /*
    ** Test case which defines computed field with expression that involves more than one column
    */

    /*-------------------*/
    /* Computed by (a*b) */
    /*-------------------*/
    create table t0 (a integer, b integer, a_b computed by (a*b));
    commit; -- t0;
    insert into t0(a,b) values(10,10);
    insert into t0(a,b) values(11,11);
    select 'Passed 1 - Insert' from t0 where a_b = a*b having count(*) = 2;

    update t0 set a = 12, b = 12 where a = 10;
    update t0 set a = 13         where a = 11;
    select 'Passed 1 - Update' from t0 where a_b = a*b having count(*) = 2;

    /*---------------------*/
    /* Computed by (a*b/c) */
    /*---------------------*/
    create table t5 (a integer, b integer, c integer, a_b_c computed by (a*b/c));
    commit; -- t5;
    insert into t5(a,b,c) values(10,10,10);
    insert into t5(a,b,c) values(11,11,11);
    select 'Passed 2 - Insert' from t5 where a_b_c = a*b/c having count(*) = 2;

    update t5 set a = 12, b = 12, c = 12 where a = 10;
    update t5 set a = 13                 where a = 11;
    select 'Passed 2 - Update' from t5 where a_b_c = a*b/c having count(*) = 2;

    /*----------------------*/
    /* Computed by (a/10*b) */
    /*----------------------*/
    create table t10 (a integer, b integer, a_b_const computed by (a/10*b));
    commit; -- t10;
    insert into t10(a,b) values(10,10);
    insert into t10(a,b) values(11,11);
    select 'Passed 3 - Insert' from t10 where a_b_const = a/10*b having count(*) = 2;

    update t10 set a = 12, b = 12 where a = 10;
    update t10 set a = 13         where a = 11;
    select 'Passed 3 - Update' from t10 where a_b_const = a/10*b having count(*) = 2;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Passed 1 - Insert
    Passed 1 - Update
    Passed 2 - Insert
    Passed 2 - Update
    Passed 3 - Insert
    Passed 3 - Update
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

