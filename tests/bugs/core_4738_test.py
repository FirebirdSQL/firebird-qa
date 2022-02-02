#coding:utf-8

"""
ID:          issue-5043
ISSUE:       5043
TITLE:       Command "Alter table <T> alter <C> type <domain_>" does not work:
  "BLR syntax error: expected valid BLR code at offset 15, encountered 255"
DESCRIPTION:
JIRA:        CORE-4738
FBTEST:      bugs.core_4738
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create domain dm_id int;
    commit;

    create table test(num int);
    commit;

    alter table test alter num type dm_id;
    commit;

    show table test;
"""

act = isql_act('db', test_script)

expected_stdout = """
    NUM                             (DM_ID) INTEGER Nullable
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

