#coding:utf-8

"""
ID:          new-database-17
TITLE:       New DB - RDB$LOG_FILES content
DESCRIPTION: Check the correct content of RDB$LOG_FILES in new database.
FBTEST:      functional.basic.db.17
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
set list on;
set count on;
select * from RDB$LOG_FILES;
"""

act = isql_act('db', test_script)

expected_stdout = """
    Records affected: 0
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
