#coding:utf-8
#
# id:           bugs.core_1171
# title:        isql exponential format of numbers has zero pad on windows
# decription:   
# tracker_id:   CORE-1171
# min_versions: ['2.1.3']
# versions:     2.1.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select cast ('-2.488355210669293e+39' as double precision) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                   CAST
=======================
 -2.488355210669293e+39

"""

@pytest.mark.version('>=2.1.3')
def test_core_1171_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

