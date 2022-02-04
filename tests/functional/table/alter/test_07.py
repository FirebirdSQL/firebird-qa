#coding:utf-8

"""
ID:          table.alter-07
TITLE:       ALTER TABLE - ALTER - POSITION
DESCRIPTION:
FBTEST:      functional.table.alter.07
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE test( id INTEGER NOT NULL,
                   text VARCHAR(32));
commit;
"""

db = db_factory(init=init_script)

test_script = """ALTER TABLE test ALTER text POSITION 1;
SHOW TABLE test;
"""

act = isql_act('db', test_script)

expected_stdout = """TEXT                            VARCHAR(32) Nullable
ID                              INTEGER Not Null
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
