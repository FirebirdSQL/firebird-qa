#coding:utf-8
#
# id:           bugs.core_5853
# title:        Forward-compatible expressions LOCALTIME and LOCALTIMESTAMP
# decription:   
#                   2.5.9.27115: OK, 0.375s.
#                   3.0.4.33019: OK, 0.937s.
#                   ::: NOTE :::
#                   Test for 4.0 currently is EXCLUDED because changes not yet merged in master.
#                
# tracker_id:   CORE-5853
# min_versions: ['2.5.9']
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
    set planonly;
    select current_time, current_timestamp from rdb$database;
    --select localtime from rdb$database;
    --select localtimestamp from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (RDB$DATABASE NATURAL)
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

