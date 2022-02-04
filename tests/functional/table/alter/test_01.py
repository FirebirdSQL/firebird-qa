#coding:utf-8

"""
ID:          table.alter-01
TITLE:       ALTER TABLE - ADD column
DESCRIPTION:
FBTEST:      functional.table.alter.01
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE test( id INTEGER);
commit;"""

db = db_factory(init=init_script)

test_script = """ALTER TABLE test ADD text varchar(32);
SHOW TABLE test;"""

act = isql_act('db', test_script)

expected_stdout = """ID                              INTEGER Nullable
TEXT                            VARCHAR(32) Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
