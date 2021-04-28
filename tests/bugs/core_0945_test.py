#coding:utf-8
#
# id:           bugs.core_0945
# title:        Bad error message when tring to create FK to non-existent table
# decription:   
# tracker_id:   CORE-945
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_945-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE TABLE TAB_TestA (
  UID INTEGER NOT NULL PRIMARY KEY
);

CREATE TABLE TAB_TestB (
  UID INTEGER NOT NULL PRIMARY KEY,
  TestA INTEGER CONSTRAINT FK_TestA REFERENCES TABTestA(UID) ON UPDATE CASCADE
);

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLE TAB_TESTB failed
-Table TABTESTA not found
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

