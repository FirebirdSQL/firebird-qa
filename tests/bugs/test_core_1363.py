#coding:utf-8
#
# id:           bugs.core_1363
# title:        ISQL crash when converted-from-double string longer than 23 bytes
# decription:   
# tracker_id:   CORE-1363
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select -2.488355210669293e-22 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
               CONSTANT
=======================
 -2.488355210669293e-22

"""

@pytest.mark.version('>=2.5')
def test_core_1363_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

