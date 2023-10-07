#coding:utf-8

"""
ID:          table.alter-02
TITLE:       ALTER TABLE. Add column with DEFAULT expression, NOT NULL requirement and UNIQUE constraint that must be applied to its values.
DESCRIPTION:
FBTEST:      functional.table.alter.02
NOTES:
    [07.10.2023] pzotov
    Changed datatype from text to integer (SHOW command output often changes for textual fields).
    Currently SHOW TABLE remains here but later it can be replaced with query to RDB$ tables.
"""

import pytest
from firebird.qa import *

init_script = """
    create table test(id integer);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    alter table test add pid int default current_connection not null constraint test_unq unique;
    show table test;
"""

act = isql_act('db', test_script)

expected_stdout = """
    ID                              INTEGER Nullable
    PID                             INTEGER Not Null default current_connection
    CONSTRAINT TEST_UNQ:
    Unique key (PID)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
