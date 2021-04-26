#coding:utf-8
#
# id:           bugs.core_1126
# title:        UNION vs UTF8 literals : arithmetic exception is thrown
# decription:   
# tracker_id:   CORE-1126
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1126

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT _UTF8 'Z' FROM RDB$DATABASE
UNION ALL
SELECT _UTF8 'A' FROM RDB$DATABASE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """CONSTANT
========
Z
A

"""

@pytest.mark.version('>=2.5')
def test_core_1126_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

