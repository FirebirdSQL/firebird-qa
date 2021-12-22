#coding:utf-8
#
# id:           functional.intfunc.string.position_02
# title:        Test Position
# decription:   
# tracker_id:   CORE-1511
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.string.position_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT POSITION('beau','beau,il fait beau') C1,POSITION('beau','beau,il fait beau',2) C2 FROM RDB$DATABASE;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          C1           C2
============ ============
           1           14
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

