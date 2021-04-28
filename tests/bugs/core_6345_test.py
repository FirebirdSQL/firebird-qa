#coding:utf-8
#
# id:           bugs.core_6345
# title:        Server crashes on overflow of division result
# decription:   
#                   Confirmed bug on 4.0.0.2076, 3.0.6.33322
#                   Checked on 4.0.0.2078, 3.0.6.33326 - all OK.
#                   (intermediate snapshots with timestamps: 26.06.20 06:36, 07:26)
#                
# tracker_id:   CORE-6345
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select -922337203685477.5808/-1.0 from rdb$database; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    Integer overflow.  The result of an integer operation caused the most significant bit of the result to carry.
  """

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

