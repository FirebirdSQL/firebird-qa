#coding:utf-8
#
# id:           bugs.core_1329
# title:        size of alias name in a table
# decription:   Bug with size of alias name in a table (but still minor that 31 characters)
# tracker_id:   CORE-1329
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_1329

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE TABLE BIG_TABLE_1234567890123 (COD INTEGER NOT NULL PRIMARY KEY);
COMMIT;
SELECT
BIG_TABLE_1234567890123.COD
FROM
BIG_TABLE_1234567890123
JOIN (SELECT
      BIG_TABLE_1234567890123.COD
      FROM
      BIG_TABLE_1234567890123) BIG_TABLE_1234567890123_ ON
BIG_TABLE_1234567890123.COD = BIG_TABLE_1234567890123_.COD;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.0.1')
def test_1(act_1: Action):
    act_1.execute()

