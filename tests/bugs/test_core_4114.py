#coding:utf-8
#
# id:           bugs.core_4114
# title:        SIMILAR TO does not work with x-prefixed literals
# decription:   
#                   Checked on:
#                   2.5.9.27115: OK, 1.390s.
#                   3.0.4.32972: OK, 3.594s.
#                   4.0.0.1201: OK, 2.875s.
#                
# tracker_id:   CORE-4114
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select
      iif(' ' similar to '[[:WHITESPACE:]]', 'T', 'F') as f1,
      iif(_win1252 x'20' similar to '[[:WHITESPACE:]]', 'T', 'F') as f2,
      iif(_win1252 x'20' similar to '%', 'T', 'F') as f3
    from RDB$DATABASE ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F1                              T
    F2                              T
    F3                              T
  """

@pytest.mark.version('>=2.5.0')
def test_core_4114_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

