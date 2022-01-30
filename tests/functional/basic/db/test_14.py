#coding:utf-8

"""
ID:          new-database-14
TITLE:       New DB - RDB$CHECK_CONSTRAINTS
DESCRIPTION: Check for correct content of RDB$CHECK_CONSTRAINTS in new database.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set count on;
    select * from rdb$check_constraints
    order by
        rdb$constraint_name
        ,rdb$trigger_name
    ;
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
