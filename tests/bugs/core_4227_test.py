#coding:utf-8

"""
ID:          issue-4551
ISSUE:       4551
TITLE:       Regression: Wrong evaluation of BETWEEN and boolean expressions due to parser conflict
DESCRIPTION:
JIRA:        CORE-4227
NOTES:
    [14.06.2026] pzotov
    Replaced source for test query: use regular user table rather than rdb$database which now stores
    rdb$relation_id = 0 for all 6.x snapshots since 21-may-2026m (see #bb280120: generator is used
    to store rdb$relation_id for new relations rather than this column).
    Confirmed bug on 3.0.0.30653-46f93fa, got "SQLSTATE = 22000 / ... / -Invalid usage of boolean ..."
    (check possible only using command prompt and ISQL; not in this QA).
    Bug was fixed in #39bccae7 (Sep 18 16:33:59 2013 +0000).
    Checked on 3.0.0.30653-39bccae -- all fine.

    Checked on 6.0.0.2002; 5.0.5.1826; 4.0.8.3279; 3.0.14.33855.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    recreate table test (rel_id int, rel_descr blob);
    insert into test values(128,null);
    select * from test where rel_id between 1 and 500 and rel_descr is null;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    REL_ID    128
    REL_DESCR <null>
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
