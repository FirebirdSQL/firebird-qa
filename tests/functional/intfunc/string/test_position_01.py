#coding:utf-8
#
# id:           functional.intfunc.string.position_01
# title:        test for POSITION function
# decription:   POSITION( <string> IN <string> )
#               
#               POSITION(X IN Y) returns the position of the substring X in the string Y. Returns 0 if X is not found within Y.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.string.position_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ select position('beau' IN 'il fait beau dans le nord' ) from rdb$database;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """          POSITION
      ============
                 9"""

@pytest.mark.version('>=2.1')
def test_position_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

