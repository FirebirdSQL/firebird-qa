#coding:utf-8
#
# id:           functional.intfunc.string.overlay_01
# title:        test for OVERLAY function
# decription:   OVERLAY  See below  Returns string1 replacing the substring FROM start FOR length by string2.
#               
#               
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.string.overlay_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ select  OVERLAY( 'il fait beau dans le sud  de la france' PLACING 'NORD' FROM 22 for 4 ) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """      OVERLAY
      ==========================================
      il fait beau dans le NORD de la france
"""

@pytest.mark.version('>=2.1')
def test_overlay_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

