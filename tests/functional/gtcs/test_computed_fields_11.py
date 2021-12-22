#coding:utf-8
#
# id:           functional.gtcs.computed_fields_11
# title:        computed-fields-11
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_11.script
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

substitutions_1 = [('^((?!Statement failed|SQL error code|Column unknown|F01|F02|REL_NAME|Records).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    set list on;
    set count on;

    /*-----------------------------------------*/
    /* Computed field using non-existing field */
    /*-----------------------------------------*/
    create table t0 (f01 integer, f_calc computed by (f02));

    /*--------------------------------------------*/
    /* Computed field using not yet defined field */
    /*--------------------------------------------*/
    create table t1 (f_calc computed by (f01), f01 integer);

    recreate table t2(f01 int, f99 int);
    commit;
    alter table t2
        add f_calc computed by( f01 + f99)
        ,alter f99 position 3 -- MUST PASS! FB 3+ will produce correct script if we want to extract metadata using isql -x.
        --,drop f99 -- Statement failed, SQLSTATE = 42S22 / invalid request BLR at offset 13 / -column f99 is not defined in table T2
    ;
    commit;

    select r.rdb$relation_name as rel_name
    from rdb$relations r
    where r.rdb$relation_name in ( upper('t0'), upper('t1'), upper('t2')  )
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    REL_NAME T2
    Records affected: 1
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    unsuccessful metadata update
    -CREATE TABLE T0 failed
    -Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -F02

    Statement failed, SQLSTATE = 42S22
    unsuccessful metadata update
    -CREATE TABLE T1 failed
    -Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -F01
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

    assert act_1.clean_stdout == act_1.clean_expected_stdout

