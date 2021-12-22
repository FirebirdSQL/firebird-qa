#coding:utf-8
#
# id:           bugs.core_1386
# title:        Generated columns
# decription:   
# tracker_id:   CORE-1386
# min_versions: []
# versions:     2.1.0
# qmid:         bugs.core_1386

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE TABLE TAB1 (COL1 INTEGER, COL2 GENERATED ALWAYS AS (COL1 +1), COL3 INTEGER GENERATED ALWAYS AS (COL1 +1));
COMMIT;
SHOW TABLE TAB1;
INSERT INTO TAB1 (COL1) VALUES (1);
COMMIT;
SELECT * FROM TAB1;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """COL1                            INTEGER Nullable
COL2                            Computed by: (COL1 +1)
COL3                            Computed by: (COL1 +1)

        COL1                  COL2         COL3
============ ===================== ============
           1                     2            2

"""

@pytest.mark.version('>=2.1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

