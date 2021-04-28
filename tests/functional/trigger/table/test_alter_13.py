#coding:utf-8
#
# id:           functional.trigger.table.alter_13
# title:        ALTER TRIGGER - AS
# decription:   ALTER TRIGGER - AS
#               Try use new prefix in DELETE trigger
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               CREATE TRIGGER
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.trigger.alter.alter_trigger_13

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('At line.*', '')]

init_script_1 = """
    create table test( id integer not null constraint unq unique, text varchar(32));
    commit;
    set term ^;
    create trigger tg for test before delete position 1 as
    begin
    end ^
    set term ;^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Since WI-T3.0.0.31733 content of STDERR has been changed: source position of
    -- problematic statement is displayed now on seperate line, like this:
    -- "-At line 4, column 1"
    -- Decided to suppress this line.
    set term ^;
    alter trigger tg as
    begin
      new.text='altered trigger';
    end ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    unsuccessful metadata update
    -ALTER TRIGGER TG failed
    -Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -NEW.TEXT
    -At line 4, column 5
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

