#coding:utf-8
#
# id:           bugs.core_1343
# title:        Bug with a simple case and a subquery
# decription:   
# tracker_id:   CORE-1343
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """--works fine (searched case with a subquery)

SELECT
  CASE
    WHEN (SELECT 'A' FROM RDB$DATABASE) = 'A' THEN
      'Y'
    WHEN (SELECT 'A' FROM RDB$DATABASE) = 'B' THEN
      'B'
    ELSE
      'N'
  END
FROM RDB$DATABASE;

--works fine (simple case without a subquery)
SELECT
  CASE 'A'
    WHEN 'A' THEN
      'Y'
    WHEN 'B' THEN
      'N'
    ELSE
      'U'
    END
FROM RDB$DATABASE;

--don't work (simple case with a subquery)
SELECT
  CASE (SELECT 'A' FROM RDB$DATABASE)
    WHEN 'A' THEN
      'Y'
    WHEN 'B' THEN
      'N'
    ELSE
      'U'
   END
FROM RDB$DATABASE;

/*
Invalid token.
invalid request BLR at offset 110.
context already in use (BLR error).
*/
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
CASE
======
Y


CASE
======
Y


CASE
======
Y

"""

@pytest.mark.version('>=2.5')
def test_core_1343_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

