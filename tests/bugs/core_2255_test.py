#coding:utf-8
#
# id:           bugs.core_2255
# title:        '...exception...string right truncation' when alter view with join
# decription:   
# tracker_id:   CORE-2255
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST_VARCHAR (
    ID INTEGER,
    CAPTION VARCHAR(1024)
);

INSERT INTO TEST_VARCHAR (ID, CAPTION) VALUES (1, 'CAP_1');

CREATE VIEW P_TEST_VARCHAR(
    ID,
    CAPTION)
AS
SELECT
    T1.ID,
    T1.CAPTION
FROM TEST_VARCHAR T1;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER VIEW P_TEST_VARCHAR(
    ID)
AS
SELECT
    T1.ID
FROM TEST_VARCHAR T1, TEST_VARCHAR T2
  WHERE T1.ID = T2.ID;

SELECT * FROM P_TEST_VARCHAR;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID
============
           1

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

