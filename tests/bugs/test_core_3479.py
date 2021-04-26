#coding:utf-8
#
# id:           bugs.core_3479
# title:        ASCII_VAL raises error instead of return 0 for empty strings
# decription:   Added two expressions with "non-typical" arguments
# tracker_id:   CORE-3479
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select ascii_val('') v1, ascii_val(ascii_char(0)) v2, ascii_val(ascii_char(null)) v3 from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    V1                              0
    V2                              0
    V3                              <null>
  """

@pytest.mark.version('>=2.5.1')
def test_core_3479_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

