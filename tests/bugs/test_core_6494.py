#coding:utf-8
#
# id:           bugs.core_6494
# title:        Inconsistent translation "string->timestamp->string->timestamp" in dialect 1
# decription:   
#                   Confirmed bug on: 4.0.0.2406, 3.0.8.33441.
#                   Checked on: 4.0.0.2416, 3.0.8.33445 - all fine.
#                 
# tracker_id:   CORE-6494
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """
    set heading off;
    select cast(cast(cast(cast('2-dec-0083' as timestamp) as varchar(64))as timestamp)as varchar(64)) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    02-DEC-0083
  """

@pytest.mark.version('>=3.0.8')
def test_core_6494_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

