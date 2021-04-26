#coding:utf-8
#
# id:           bugs.core_5705
# title:        Store precision of DECFLOAT in RDB$FIELDS
# decription:   
#                     Checked on LI-T4.0.0.940.
#                 
# tracker_id:   CORE-5705
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
    set count on;
    create domain dm_df16 as decfloat(16);
    create domain dm_df34 as decfloat(34);
    commit;
    select rdb$field_name, rdb$field_precision 
    from rdb$fields 
    where rdb$field_name in (upper('dm_df16'), upper('dm_df34')) 
    order by 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  DM_DF16                                                                                                                                                            
    RDB$FIELD_PRECISION             16

    RDB$FIELD_NAME                  DM_DF34                                                                                                                                                            
    RDB$FIELD_PRECISION             34

    Records affected: 2
  """

@pytest.mark.version('>=4.0')
def test_core_5705_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

