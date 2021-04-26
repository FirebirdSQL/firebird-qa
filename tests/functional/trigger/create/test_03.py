#coding:utf-8
#
# id:           functional.trigger.create.03
# title:        CREATE TRIGGER BEFORE UPDATE
# decription:   CREATE TRIGGER BEFORE UPDATE
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.trigger.create.create_trigger_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """CREATE TABLE tb(id INT);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
CREATE TRIGGER test FOR tb BEFORE UPDATE AS
BEGIN
  new.id=1;
END^
SET TERM ;^
SHOW TRIGGER test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Triggers on Table TB:
TEST, Sequence: 0, Type: BEFORE UPDATE, Active
AS
BEGIN
  new.id=1;
END
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

@pytest.mark.version('>=1.0')
def test_03_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

