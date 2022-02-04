#coding:utf-8

"""
ID:          table.alter-05
TITLE:       ALTER TABLE - ALTER - TO
DESCRIPTION:
FBTEST:      functional.table.alter.05
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE test( id INTEGER NOT NULL);
commit;
"""

db = db_factory(init=init_script)

test_script = """ALTER TABLE test ALTER id TO new_col_name;
SHOW TABLE test;
"""

act = isql_act('db', test_script)

expected_stdout = """NEW_COL_NAME                    INTEGER Not Null
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
