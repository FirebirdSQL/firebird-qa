#coding:utf-8
#
# id:           bugs.core_1152
# title:        cannot erase a table with check constraints referencing more than a single columns
# decription:   
# tracker_id:   CORE-1152
# min_versions: []
# versions:     2.0
# qmid:         bugs.core_1152

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test(
int1 INTEGER,
int2 INTEGER,
CHECK(int1 IS NULL OR int2 IS NULL)
);
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DROP TABLE test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.execute()

