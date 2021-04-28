#coding:utf-8
#
# id:           bugs.core_1428
# title:        Incorrect timestamp substraction in 3 dialect when result is negative number
# decription:   
# tracker_id:   CORE-1428
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1428

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT (CAST('2007-08-22 00:00:00.0019' AS TIMESTAMP) - CAST('2007-08-22 00:00:00.0000' AS TIMESTAMP)) *86400*10000 AS A
  FROM RDB$DATABASE;
SELECT (CAST('2007-08-22 00:00:00.0000' AS TIMESTAMP) - CAST('2007-08-22 00:00:00.0019' AS TIMESTAMP)) *86400*10000 AS A
  FROM RDB$DATABASE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                    A
=====================
         19.008000000


                    A
=====================
        -19.008000000

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

