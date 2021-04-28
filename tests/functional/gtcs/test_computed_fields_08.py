#coding:utf-8
#
# id:           functional.gtcs.computed_fields_08
# title:        computed-fields-08
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_08.script
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
    set bail on;
    set heading off;
    /*----------------------*/
    /* Computed by UPPER(a) */
    /*----------------------*/
    create table t0 (a char(25), upper_a computed by (upper(a)));
    commit; -- t0;
    insert into t0(a) values('abcdef');
    insert into t0(a) values('ABCDEF');
    insert into t0(a) values('123456');
    insert into t0(a) values('aBcDeF');
    select 'Passed 1 - Insert' from t0 where upper_a = upper(a) having count(*) = 4;

    update t0 set a = 'xyz' where a = 'abc';
    select 'Passed 1 - Update' from t0 where upper_a = upper(a) having count(*) = 4;

    /*-----------------------------------*/
    /* Computed by a || UPPER('upper()') */
    /*-----------------------------------*/
    create table t5 (a char(25), upper_const computed by (a || upper('upper()')));
    commit; -- t5;
    insert into t5(a) values('abcdef');
    insert into t5(a) values('ABCDEF');
    insert into t5(a) values('123456');
    insert into t5(a) values('aBcDeF');
    select 'Passed 2 - Insert' from t5 where upper_const = a || upper('upper()') having count(*) = 4;

    update t5 set a = 'xyz' where a = 'abcdef';
    select 'Passed 2 - Update' from t5 where upper_const = a || upper('upper()') having count(*) = 4;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Passed 1 - Insert
    Passed 1 - Update
    Passed 2 - Insert
    Passed 2 - Update
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

