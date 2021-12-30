#coding:utf-8
#
# id:           bugs.gh_6832
# title:        Segfault using "commit retaining" with GTT
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6832
#               
#                   Confirmed crash on 5.0.0.40 CS, 5.0.0.47 SS.
#                   Checked on 5.0.0.56 SS/CS - all OK.
#                   Checked on 4.0.0.2502 (intermediate snapshot, 01.06.2020 16:49).
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
    set autoddl off;
    recreate global temporary table gtt(x int);
    commit retain;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
