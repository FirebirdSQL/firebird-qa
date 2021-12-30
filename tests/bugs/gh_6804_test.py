#coding:utf-8
#
# id:           bugs.gh_6804
# title:        assertion in tomcrypt when key length for rc4 too small
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6804
#               
#                   Confirmed crahs on 4.0.0.2453.
#                   Checked on 4.0.0.2479; 5.0.0.20 -- all OK.
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
    set blob all;
    set list on;
    select encrypt('abc' using rc4 key 'qq') from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22023
    Invalid key length 2, need >4
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
