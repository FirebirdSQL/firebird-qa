#coding:utf-8
#
# id:           functional.trigger.alter.01
# title:        ALTER TRIGGER - ACTIVE
# decription:   ALTER TRIGGER - ACTIVE
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               CREATE TRIGGER
#               SHOW TRIGGER
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.trigger.alter.alter_trigger_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """CREATE TABLE test( id INTEGER NOT NULL CONSTRAINT unq UNIQUE,
                   text VARCHAR(32));
commit;
SET TERM ^;
CREATE TRIGGER tg FOR test INACTIVE BEFORE INSERT
AS
BEGIN
  new.id=1;
END ^
SET TERM ;^
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER TRIGGER tg ACTIVE;
SHOW TRIGGER tg;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Triggers on Table TEST:
TG, Sequence: 0, Type: BEFORE INSERT, Active
AS
BEGIN
  new.id=1;
END
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

@pytest.mark.version('>=1.0')
def test_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

