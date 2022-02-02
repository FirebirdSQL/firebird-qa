#coding:utf-8

"""
ID:          issue-353
ISSUE:       353
TITLE:       Bug with ALL keyword
DESCRIPTION:
JIRA:        CORE-115
FBTEST:      bugs.core_0115
"""

import pytest
from firebird.qa import *

# version: 2.5
# resources: None

db = db_factory()

test_script = """
    recreate table test (i int not null);

    insert into test values (2);
    insert into test values (3);
    commit;

    set plan on;

    set count on;
    select * from test where 1 > all(select i from test);

    commit;

    alter table test add constraint test_pk primary key(i) using index test_pk;
    commit;

    select * from test where i > all(select i from test);
    select * from test where i > 0 and i > all(select i from test where i > 0);

    set count off;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    Records affected: 0

    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    Records affected: 0

    PLAN (TEST INDEX (TEST_PK))
    PLAN (TEST INDEX (TEST_PK))
    Records affected: 0
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

