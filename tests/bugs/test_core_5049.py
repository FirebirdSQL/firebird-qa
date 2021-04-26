#coding:utf-8
#
# id:           bugs.core_5049
# title:        Regression: incorrect calculation of byte-length for view columns
# decription:   
# tracker_id:   CORE-5049
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Confirmed:
    -- 1) FAULT on WI-V3.0.0.32208. 
    -- 2) SUCCESS on LI-V3.0.0.32233, Rev: 62699.
    create or alter view v_test as
    select
       cast(rdb$character_set_name as varchar(2000)) as test_f01
      ,cast(rdb$character_set_name as varchar(2000)) as test_f02
      ,cast(rdb$character_set_name as varchar(2000)) as test_f03
    from
      rdb$database
    rows 1;
    
    set sqlda_display on;
    set list on;
    select * from v_test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 8000 charset: 4 UTF8
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 8000 charset: 4 UTF8
    03: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 8000 charset: 4 UTF8
  """

@pytest.mark.version('>=3.0')
def test_core_5049_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

