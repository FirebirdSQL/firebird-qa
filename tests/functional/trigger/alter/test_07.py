#coding:utf-8
#
# id:           functional.trigger.alter.07
# title:        ALTER TRIGGER - AFTER INSERT
# decription:   
#                   ALTER TRIGGER - AFTER INSERT
#               
#                   Dependencies:
#                   CREATE DATABASE
#                   CREATE TABLE
#                   CREATE TRIGGER
#                   SHOW TRIGGER
#               
#                   Checked on:
#                     2.5.9.27115: OK, 0.484s.
#                     3.0.4.33021: OK, 1.000s.
#                     4.0.0.1143: OK, 2.203s.
#                   NB: phrase 'attempted update of read-only column' contains name of table and column ('TEST.ID') on 4.0.x
#                 
# tracker_id:   
# min_versions: []
# versions:     4.0.0
# qmid:         functional.trigger.alter.alter_trigger_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.0
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """
    CREATE TABLE test( id INTEGER NOT NULL CONSTRAINT unq UNIQUE, text VARCHAR(32));
    SET TERM ^;
    CREATE TRIGGER tg FOR test BEFORE UPDATE
    AS
    BEGIN
      new.id=1;
    END ^
    SET TERM ;^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    ALTER TRIGGER tg AFTER INSERT;
    SHOW TRIGGER tg;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Triggers on Table TEST:
    TG, Sequence: 0, Type: BEFORE UPDATE, Active
    AS
    BEGIN
      new.id=1;
    END
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column TEST.ID
  """

@pytest.mark.version('>=4.0.0')
def test_07_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

