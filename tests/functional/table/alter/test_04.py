#coding:utf-8

"""
ID:          table.alter-04
TITLE:       ALTER TABLE - ADD CONSTRAINT - UNIQUE
DESCRIPTION:
FBTEST:      functional.table.alter.04
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE test( id INTEGER NOT NULL);
commit;"""

db = db_factory(init=init_script)

test_script = """ALTER TABLE test ADD CONSTRAINT unq UNIQUE(id);
SHOW TABLE test;"""

act = isql_act('db', test_script)

expected_stdout = """ID                              INTEGER Not Null
CONSTRAINT UNQ:
Unique key (ID)"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
