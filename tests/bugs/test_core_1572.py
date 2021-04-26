#coding:utf-8
#
# id:           bugs.core_1572
# title:        Multiple Rows in Singleton Select not reported in a View
# decription:   
# tracker_id:   CORE-1572
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_1572-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TABLE1 ( ID1 INTEGER NOT NULL, FIELD1 VARCHAR(20));
CREATE TABLE TABLE2 ( ID2 INTEGER NOT NULL, FIELD2 VARCHAR(20));

INSERT INTO TABLE1 (ID1, FIELD1) VALUES (1, 'ONE');
INSERT INTO TABLE2 (ID2, FIELD2) VALUES (2, 'TWO');
INSERT INTO TABLE2 (ID2, FIELD2) VALUES (3, 'THREE');

CREATE VIEW VIEW_TABLE( ID1, FIELD1, FIELD2) AS
SELECT TABLE1.ID1, TABLE1.FIELD1, ( SELECT TABLE2.FIELD2 FROM TABLE2 ) FROM TABLE1;
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT * FROM VIEW_TABLE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
         ID1 FIELD1               FIELD2
============ ==================== ====================
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 21000
multiple rows in singleton select
"""

@pytest.mark.version('>=2.5.0')
def test_core_1572_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

