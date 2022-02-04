#coding:utf-8

"""
ID:          new-database-05
TITLE:       New DB - RDB$DEPENDENCIES
DESCRIPTION: Check for correct content of RDB$DEPENDENCIES in new database.
FBTEST:      functional.basic.db.05
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set count on;
    select * from rdb$dependencies
    order by
        rdb$dependent_name
        ,rdb$depended_on_name
        ,rdb$field_name
        ,rdb$dependent_type
        ,rdb$depended_on_type
        ,rdb$package_name -- avail. only for FB 3.0+
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
    Records affected: 0
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
