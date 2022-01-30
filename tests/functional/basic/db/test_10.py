#coding:utf-8

"""
ID:          new-database-10
TITLE:       New DB - RDB$FORMATS
DESCRIPTION: Check for correct content of RDB$FORMATS in new database.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set count on;
    set blob all;
    select * from rdb$formats
    order by
        rdb$relation_id
        ,rdb$format
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
