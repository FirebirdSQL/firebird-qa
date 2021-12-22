#coding:utf-8
#
# id:           functional.trigger.create.17
# title:        CREATE TRIGGER SQL2003
# decription:   CREATE TRIGGER SQL2003
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.trigger.create.create_trigger_17

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """
    CREATE TABLE tb(id INT);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    SET TERM ^;
    /* Tested command: */
    CREATE TRIGGER test BEFORE INSERT
    ON tb AS
    BEGIN
        new.id=1;
    END^
    SET TERM ;^
    SHOW TRIGGER test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Triggers on Table TB:
    TEST, Sequence: 0, Type: BEFORE INSERT, Active
    AS
    BEGIN
      new.id=1;
    END
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

