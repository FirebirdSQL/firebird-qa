#coding:utf-8
#
# id:           functional.gtcs.computed_fields_03
# title:        computed-fields-03
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_03.script
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
    ** Syntax test cases - Valid string operations
    */

    /*-----------------*/
    /* Computed by (s) */
    /*-----------------*/
    create table t0  (s char(25), sc computed by (s));
    commit; -- t0;
    insert into t0(s) values('computed');
    insert into t0(s) values('(s)');
    select 'Passed 1 - Insert' from t0 where sc = s having count(*) = 2;

    update t0 set s = 'by' where s = 'computed';
    select 'Passed 1 - Update' from t0 where sc = s having count(*) = 2;

    /*--------------------*/
    /* Computed by (s||s) */
    /*--------------------*/
    create table t5 (s char(25), sc computed by (s||s));
    commit; -- t5;
    insert into t5(s) values('computed');
    insert into t5(s) values('(s)');
    select 'Passed 2 - Insert' from t5 where sc = s||s having count(*) = 2;

    update t5 set s = 'by' where s = 'computed';
    select 'Passed 2 - Update' from t5 where sc = s||s having count(*) = 2;

    /*-------------------*/
    /* Computed by (s|s) */
    /*-------------------*/
    /*
    ** Bug 6604: Use of "|" as concat operator not working
    **
    create table t10 (s char(25), sc computed by (s|s))
    commit; -- t10
    insert into t10(s) values('computed')
    insert into t10(s) values('(s)')
    select 'Passed 3 - Insert' from t10 where sc = s|s having count(*) = 2

    update t10 set s = 'by' where s = 'computed'
    select 'Passed 3 - Update' from t10 where sc = s|s having count(*) = 2
    */

    /*--------------------------*/
    /* Computed by (s||' test') */
    /*--------------------------*/
    create table t15 (s char(25), sc computed by (s||' test'));
    commit; -- t15;
    insert into t15(s) values('computed');
    insert into t15(s) values('(s||'' test'')');
    select 'Passed 4 - Insert' from t15 where sc = s||' test' having count(*) = 2;

    update t15 set s = 'by' where s = 'computed';
    select 'Passed 4 - Update' from t15 where sc = s||' test' having count(*) = 2;

    /*--------------------------*/
    /* Computed by ('test '||s) */
    /*--------------------------*/
    create table t20 (s char(25), sc computed by ('test '||s));
    commit; -- t20;
    insert into t20(s) values('computed');
    insert into t20(s) values('(''test ''||s)');
    select 'Passed 5 - Insert' from t20 where sc = 'test '||s having count(*) = 2;

    update t20 set s = 'by' where s = 'computed';
    select 'Passed 5 - Update' from t20 where sc = 'test '||s having count(*) = 2;

    /*-----------------------------------*/
    /* Computed by ('test '||s||' test') */
    /*-----------------------------------*/
    create table t25 (s char(25), sc computed by ('test '||s||' test'));
    commit; -- t25;
    insert into t25(s) values('computed');
    insert into t25(s) values('(''test ''||s||'' test'')');
    select 'Passed 6 - Insert' from t25 where sc = 'test '||s||' test' having count(*) = 2;

    update t25 set s = 'by' where s = 'computed';
    select 'Passed 6 - Update' from t25 where sc = 'test '||s||' test' having count(*) = 2;

    /*----------------------*/
    /* Computed by ('test') */
    /*----------------------*/
    create table t30 (s char(25), sc computed by ('test'));
    commit; -- t30;
    insert into t30(s) values('computed');
    insert into t30(s) values('(''test'')');
    select 'Passed 7 - Insert' from t30 where sc = 'test' having count(*) = 2;

    update t30 set s = 'by' where s = 'computed';
    select 'Passed 7 - Update' from t30 where sc = 'test' having count(*) = 2;

    /*--------------------------------*/
    /* Computed by ('test '||' test') */
    /*--------------------------------*/
    create table t35 (s char(25), sc computed by ('test '||' test'));
    commit; -- t35;
    insert into t35(s) values('computed');
    insert into t35(s) values('(''test ''||'' test'')');
    select 'Passed 8 - Insert' from t35 where sc = 'test '||' test' having count(*) = 2;

    update t35 set s = 'by' where s = 'computed';
    select 'Passed 8 - Update' from t35 where sc = 'test '||' test' having count(*) = 2;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Passed 1 - Insert
    Passed 1 - Update
    Passed 2 - Insert
    Passed 2 - Update
    Passed 4 - Insert
    Passed 4 - Update
    Passed 5 - Insert
    Passed 5 - Update
    Passed 6 - Insert
    Passed 6 - Update
    Passed 7 - Insert
    Passed 7 - Update
    Passed 8 - Insert
    Passed 8 - Update
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

