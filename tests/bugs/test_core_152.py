#coding:utf-8
#
# id:           bugs.core_152
# title:        Sqlsubtype incorrect on timestamp math, constant arithmetic
# decription:   
# tracker_id:   CORE-152
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_152

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype|DTS_DIFF).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display;
    set list on;
    select current_timestamp - current_timestamp dts_diff from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 580 INT64 scale: -9 subtype: 1 len: 8
    :  name: SUBTRACT  alias: DTS_DIFF
    DTS_DIFF 0.000000000
  """

@pytest.mark.version('>=3.0')
def test_core_152_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

