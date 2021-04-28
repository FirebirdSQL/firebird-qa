#coding:utf-8
#
# id:           bugs.core_1802
# title:        Maximum key size using PXW_CSY collation
# decription:   
# tracker_id:   CORE-1802
# min_versions: []
# versions:     2.5.3
# qmid:         bugs.core_1802

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE TABLE TAB21(
  ID INTEGER,
  A VARCHAR(490) CHARACTER SET WIN1250 COLLATE PXW_CSY,
  CONSTRAINT CU UNIQUE(A) );
COMMIT;
SHOW INDEX CU;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """CU UNIQUE INDEX ON TAB21(A)
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

