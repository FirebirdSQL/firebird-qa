#coding:utf-8
#
# id:           bugs.core_1489
# title:        DATEADD wrong work with NULL arguments
# decription:   
# tracker_id:   CORE-1489
# min_versions: []
# versions:     2.1.0
# qmid:         bugs.core_1489

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT 1, DATEADD(SECOND, Null, CAST('01.01.2007' AS DATE)) FROM RDB$DATABASE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CONSTANT     DATEADD
============ ===========
           1      <null>

"""

@pytest.mark.version('>=2.1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

