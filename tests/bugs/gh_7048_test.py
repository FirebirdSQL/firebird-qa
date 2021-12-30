#coding:utf-8
#
# id:           bugs.gh_7048
# title:        Release of user savepoint releases too much
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/7048
#               
#                   Confirmed bug on 4.0.1.2668
#                   Checked on 4.0.1.2672 - all fine.
#                
# tracker_id:   
# min_versions: ['4.0.1']
# versions:     4.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    savepoint a;
    savepoint b;
    release savepoint b;
    release savepoint a;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

@pytest.mark.version('>=4.0.1')
def test_1(act_1: Action):
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
