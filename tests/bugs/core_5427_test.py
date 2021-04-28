#coding:utf-8
#
# id:           bugs.core_5427
# title:        Error on field concatenation of System tables
# decription:   
#                   Confirmed bug on WI-T4.0.0.469, got:
#                      arithmetic exception, numeric overflow, or string truncation
#                      -string right truncation
#                      -expected length 75, actual 264
#                   Checked on WI-T4.0.0.470 - works fine.
#                
# tracker_id:   CORE-5427
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select 0*char_length(txt) x1, 0*octet_length(txt) x2
    from (
      select 'generator '|| r.rdb$generator_name ||' .' as txt from rdb$generators r
      order by 1 rows 1
    )
    ; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X1                              0 
    X2                              0 
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

