#coding:utf-8
#
# id:           bugs.gh_6786
# title:        Add session time zone to system context.
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6786
#                   
#                   Test checks only presence of not-null context variable in the 'SYSTEM' namespace,
#                   without verifying its value (obviously, it can vary on different machines).
#                   Name of context variable: 'SESSION_TIMEZONE'.
#               
#                   Checked on intermediate build 4.0.0.2453 (timestamp: 04-may-2021 15:53).
#                
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select iif(rdb$get_context('SYSTEM','SESSION_TIMEZONE') is not null, 'Defined.','UNDEFINED,') as session_tz from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SESSION_TZ                      Defined.
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
