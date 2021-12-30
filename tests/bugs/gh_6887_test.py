#coding:utf-8
#
# id:           bugs.gh_6887
# title:        Invalid SIMILAR TO patterns may lead memory read beyond string limits
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6887
#               
#                   On 5.0.0.88 and 4.0.1.2523 expression marked as [ 2 ] raises:
#                   "SQLSTATE = 22025/Invalid ESCAPE sequence",
#                   After fix its error became the same as for [ 1 ].
#               
#                   NB: backslash character must be duplicated when SQL script is launched from Python,
#                   in contrary to common usage (pass script to ISQL utility from OS command prompt).
#               
#                   Checked on: 5.0.0.113, 4.0.1.2539.
#                
# tracker_id:   
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
    select '1' similar to '1[a-' from rdb$database; ----------------------- [ 1 ]

    -- NOTE: we have to DUPLICATE backslash here otherwise Python
    -- framework will 'swallow' it and error message will differ.
    -- Single backslash must be used if this expression is passed
    -- to ISQL from OS command prompt or using '-i' command switch:
    select '1' similar to '1\\' escape '\\' from rdb$database; ------------ [ 2 ]
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Invalid SIMILAR TO pattern

    Statement failed, SQLSTATE = 42000
    Invalid SIMILAR TO pattern
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
