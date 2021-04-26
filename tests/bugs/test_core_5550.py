#coding:utf-8
#
# id:           bugs.core_5550
# title:        Computed decimal field in a view has wrong RDB$FIELD_PRECISION
# decription:   
#                   30SS, build 3.0.3.32738: OK, 0.828s.
#                   40SS, build 4.0.0.680: OK, 1.062s.
#                
# tracker_id:   CORE-5550
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate view v_test(f) as 
    select cast(null as decimal(10,2)) 
    from rdb$database;
    commit;

    set list on;
    set count on;

    select
        cast(rf.rdb$field_name as varchar(80)) rf_field_name,
        ff.rdb$field_precision ff_field_prec,
        ff.rdb$field_scale ff_field_scale
    from rdb$relation_fields rf
    join rdb$fields ff on rf.rdb$field_source =  ff.rdb$field_name
    where rf.rdb$relation_name = upper('v_test');

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RF_FIELD_NAME                   F
    FF_FIELD_PREC                   18
    FF_FIELD_SCALE                  -2
    Records affected: 1
  """

@pytest.mark.version('>=3.0.3')
def test_core_5550_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

