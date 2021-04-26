#coding:utf-8
#
# id:           bugs.core_3874
# title:        Computed column appears in non-existant rows of left join
# decription:   
# tracker_id:   CORE-3874
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST_TABLE
(
  ID INTEGER,
  COMPUTED_COL VARCHAR(6) COMPUTED BY ('FAILED')
);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT t.COMPUTED_COL
FROM RDB$DATABASE r
LEFT JOIN TEST_TABLE t
ON r.RDB$RELATION_ID = t.ID;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """COMPUTED_COL
============
<null>
"""

@pytest.mark.version('>=2.5.3')
def test_core_3874_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

