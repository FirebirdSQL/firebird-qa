#coding:utf-8
#
# id:           functional.trigger.alter.10
# title:        ALTER TRIGGER - AS
# decription:   ALTER TRIGGER - AS
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               CREATE TRIGGER
#               SHOW TRIGGER
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.trigger.alter.alter_trigger_10

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """CREATE TABLE test( id INTEGER NOT NULL CONSTRAINT unq UNIQUE,
                   text VARCHAR(32));
SET TERM ^;
CREATE TRIGGER tg FOR test BEFORE INSERT POSITION 1
AS
BEGIN
  new.text=new.text||'tg1 ';
END ^
SET TERM ;^
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
ALTER TRIGGER tg AS
BEGIN
  new.text='altered trigger';
END ^

SET TERM ;^
SHOW TRIGGER tg;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Triggers on Table TEST:
TG, Sequence: 1, Type: BEFORE INSERT, Active
AS
BEGIN
  new.text='altered trigger';
END
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

