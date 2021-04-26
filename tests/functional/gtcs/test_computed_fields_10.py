#coding:utf-8
#
# id:           functional.gtcs.computed_fields_10
# title:        computed-fields-10
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_10.script
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

    -- Test verifies COMPUTED-BY field which expression involves GEN_ID() call.

    create generator gen1;
    set generator gen1 to 1000;
    commit; -- show generator gen1;

    /*----------------------------*/
    /* Computed by (a + gen_id()) */
    /*----------------------------*/
    create table t0 (a integer, genid_field computed by (a + gen_id(gen1, 1)));
    commit; -- t0;
    insert into t0(a) values(10);
    insert into t0(a) values(12);
    select * from t0;

    set generator gen1 to 1000;
    select * from t0;

    /*
    **  Since computed fields are evaluated during run-time, the computed
    **  field with gen_id() will be different every-time. So, the following
    **  select will never have a match.
    */ 
    set generator gen1 to 1000;
    select * from t0 where genid_field = gen_id(gen1, 1);


  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    10 1011
    12 1014

    10 1011
    12 1014
  """

@pytest.mark.version('>=2.5')
def test_computed_fields_10_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

