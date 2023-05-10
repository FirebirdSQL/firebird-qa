#coding:utf-8

"""
ID:          trigger.table.alter-07
TITLE:       ALTER TRIGGER - AFTER INSERT
DESCRIPTION:
FBTEST:      functional.trigger.table.alter_07
"""

import pytest
from firebird.qa import *

init_script = """
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

db = db_factory(init=init_script)

test_script = """
    ALTER TRIGGER tg AFTER INSERT;
    SHOW TRIGGER tg;
"""

act = isql_act('db', test_script, substitutions=[('\\+.*',''),('\\=.*',''),('Trigger text.*',''), ('-attempted', 'attempted'), ('-ID',''), ('Error while parsing trigger TG\'s BLR', '')])

expected_stdout_fb3 = """
    Triggers on Table TEST:
    =============================================================================
    TG, Sequence: 0, Type: BEFORE UPDATE, Active
    Trigger text:
    =============================================================================
    AS
    BEGIN
    new.id=1;
    END
    =============================================================================
"""

expected_stderr_fb3 = """    	
    Statement failed, SQLSTATE = 2F000
    Error while parsing trigger TG's BLR
    -attempted update of read-only column
    -ID
"""

expected_stdout_fb4 =  """
    Triggers on Table TEST:
    TG, Sequence: 0, Type: BEFORE UPDATE, Active
    AS
    BEGIN
        new.id=1;
    END
"""

expected_stderr_fb4 = """
    Statement failed, SQLSTATE
    Error while parsing trigger TG's BLR
    -attempted update of read-only column TEST.ID
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    if act.is_version('>=4.0'):
        act.expected_stderr = expected_stderr_fb4
        act.expected_stdout = expected_stdout_fb4
    else:
        act.expected_stderr = expected_stderr_fb3
        act.expected_stdout = expected_stdout_fb3
    
    act.execute()
    
    assert act.clean_stdout == act.clean_expected_stdout
    assert act.clean_stderr == act.clean_expected_stderr