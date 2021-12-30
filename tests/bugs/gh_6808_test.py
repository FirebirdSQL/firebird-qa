#coding:utf-8
#
# id:           bugs.gh_6808
# title:        assertion in tomcrypt when key length for rc4 too small
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6808
#               
#                   Checked on intermediate builds 4.0.0.2481, 5.0.0.22 (timestamps: 13.05.2021 14:54 and 15:04)-- all OK.
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
    set heading off;
    select encrypt(null using aes mode cfb key 'AbcdAbcdAbcdAbcd' iv '0123456789012345') from rdb$database;
    select decrypt(null using aes mode ofb key '0123456701234567' iv '1234567890123456') from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    <null>
    <null>
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
