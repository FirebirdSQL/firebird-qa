#coding:utf-8
#
# id:           functional.trigger.alter.03
# title:        ALTER TRIGGER - BEFORE DELETE
# decription:   ALTER TRIGGER - BEFORE DELETE
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               CREATE TRIGGER
#               SHOW TRIGGER
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.trigger.alter.alter_trigger_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """CREATE TABLE test( id INTEGER NOT NULL CONSTRAINT unq UNIQUE,
                   text VARCHAR(32));
SET TERM ^;
CREATE TRIGGER tg FOR test AFTER UPDATE
AS
BEGIN
END ^
SET TERM ;^
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER TRIGGER tg BEFORE DELETE;
SHOW TRIGGER tg;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Triggers on Table TEST:
TG, Sequence: 0, Type: BEFORE DELETE, Active
AS
BEGIN
END
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

