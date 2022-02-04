#coding:utf-8

"""
ID:          new-database-27
TITLE:       New DB - RDB$TRANSACTIONS content
DESCRIPTION: Check the correct content of RDB$TRANSACTIONS in new database.
FBTEST:      functional.basic.db.27
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set count on;
    select * from rdb$transactions order by rdb$transaction_id;
"""

act = isql_act('db', test_script)

expected_stdout = """
    Records affected: 0
"""

@pytest.mark.version('>=2.5')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
