#coding:utf-8
#
# id:           bugs.core_5710
# title:        Datatype declaration DECFLOAT without precision should use a default precision
# decription:   
#                     Checked on FB40SS, build 4.0.0.943: OK, 1.625s.
#                 
# tracker_id:   CORE-5710
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table test( distance_small decfloat(16), distance_huge decfloat(34), distance_default decfloat );
    commit;

    select
         r.rdb$field_name
        ,f.rdb$field_length
        ,f.rdb$field_scale
        ,f.rdb$field_type
        ,f.rdb$field_precision
    from rdb$fields f
    join rdb$relation_fields r on f.rdb$field_name = r.rdb$field_source
    where 
        r.rdb$relation_name = upper('test')
        and r.rdb$field_name starting with upper('distance')
    order by r.rdb$field_position
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  DISTANCE_SMALL                                                                                                                                                                                                                                              
    RDB$FIELD_LENGTH                8
    RDB$FIELD_SCALE                 0
    RDB$FIELD_TYPE                  24
    RDB$FIELD_PRECISION             16

    RDB$FIELD_NAME                  DISTANCE_HUGE                                                                                                                                                                                                                                               
    RDB$FIELD_LENGTH                16
    RDB$FIELD_SCALE                 0
    RDB$FIELD_TYPE                  25
    RDB$FIELD_PRECISION             34

    RDB$FIELD_NAME                  DISTANCE_DEFAULT                                                                                                                                                                                                                                            
    RDB$FIELD_LENGTH                16
    RDB$FIELD_SCALE                 0
    RDB$FIELD_TYPE                  25
    RDB$FIELD_PRECISION             34
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

