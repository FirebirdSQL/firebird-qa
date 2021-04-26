#coding:utf-8
#
# id:           bugs.core_1528
# title:        Functions DATEDIFF does not work in dialect 1
# decription:   
# tracker_id:   CORE-1528
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1528

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """SELECT DATEDIFF(DAY, CAST('18.10.2007' AS TIMESTAMP), CAST('23.10.2007' AS TIMESTAMP)) FROM RDB$DATABASE;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
               DATEDIFF
=======================
      5.000000000000000

"""

@pytest.mark.version('>=2.1')
def test_core_1528_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

