#coding:utf-8
#
# id:           bugs.core_5097
# title:        COMPUTED-BY expressions are not converted to their field type inside the engine
# decription:   
#                
# tracker_id:   CORE-5097
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype|T2_CHECK|C1_CHECK).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test1(
        t0 timestamp default 'now'
        ,t1 timestamp computed by( 'now' )
        ,t2 computed by( extract(weekday from t1) )
    );
    recreate table test2 (n1 integer, c1 integer computed by (1.2));
    commit;

    insert into test1 default values;
    insert into test2 values (0);
    commit;

    set list on;
    set sqlda_display on;

    select * from test1 rows 0;
    select * from test2 rows 0;

    set sqlda_display off;

    select iif( t2 between 0 and 6, 1, 0 ) t2_check from test1; 
    select c1 || '' as c1_check from test2; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 510 TIMESTAMP Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 510 TIMESTAMP Nullable scale: 0 subtype: 0 len: 8
    03: sqltype: 500 SHORT Nullable scale: 0 subtype: 0 len: 2
    01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
    02: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
    T2_CHECK                        1
    C1_CHECK                        1
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

