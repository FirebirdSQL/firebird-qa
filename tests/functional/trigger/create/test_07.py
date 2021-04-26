#coding:utf-8
#
# id:           functional.trigger.create.07
# title:        CREATE TRIGGER INACTIVE AFTER DELETE
# decription:   CREATE TRIGGER INACTIVE AFTER DELETE
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.trigger.create.create_trigger_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """
    CREATE TABLE tb(id INT);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    SET TERM ^;
    CREATE TRIGGER test FOR tb INACTIVE AFTER DELETE AS
    BEGIN
    END^
    SET TERM ;^
    SHOW TRIGGER test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Triggers on Table TB:
    TEST, Sequence: 0, Type: AFTER DELETE, Inactive
    AS
    BEGIN
    END
  """

@pytest.mark.version('>=2.0')
def test_07_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

