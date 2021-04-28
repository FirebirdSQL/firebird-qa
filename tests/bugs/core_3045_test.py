#coding:utf-8
#
# id:           bugs.core_3045
# title:        "conversion error from string" after change of field type from BIGINT to VARCHAR(21)
# decription:   
# tracker_id:   CORE-3045
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST1(
  ID INTEGER,
  TEST_FIELD BIGINT,

  PRIMARY KEY(ID)
);

COMMIT;

INSERT INTO TEST1(ID, TEST_FIELD)
VALUES(1, 234);

COMMIT;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER TABLE TEST1
  ALTER TEST_FIELD TYPE VARCHAR(21);

COMMIT;

SELECT ID, TEST_FIELD
FROM TEST1
WHERE TEST_FIELD = 'A';
SELECT ID, TEST_FIELD
FROM TEST1
WHERE TEST_FIELD != 'A';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID TEST_FIELD
============ =====================
           1 234

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

