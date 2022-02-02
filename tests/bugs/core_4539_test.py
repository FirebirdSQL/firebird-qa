#coding:utf-8

"""
ID:          issue-4857
ISSUE:       4857
TITLE:       Server does not accept the right plan
DESCRIPTION:
JIRA:        CORE-4539
FBTEST:      bugs.core_4539
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table horse(
        id int primary key
       ,color_id int, name varchar(10)
    );
    recreate table color(
        id int
        ,name varchar(10)
    );
    commit;
    create index color_name on color(name);
    commit;

    -------------
    -- Confirmed on WI-T3.0.0.31374 Firebird 3.0 Beta 1
    -- Statement failed, SQLSTATE = 42000
    -- index COLOR_NAME cannot be used in the specified plan
    set planonly;
    select count(*)
    from horse h
    join color c on h.color_id = c.id
    where h.name = c.name
    plan join (h natural, c index (color_name));
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN JOIN (H NATURAL, C INDEX (COLOR_NAME))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

