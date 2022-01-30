#coding:utf-8

"""
ID:          new-database-32
TITLE:       New DB - RDB$VIEW_RELATIONS content
DESCRIPTION: Check the correct content of RDB$VIEW_RELATIONS in new database.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set count on;
    select * from rdb$view_relations v order by v.rdb$view_name, v.rdb$relation_name;
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
