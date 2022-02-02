#coding:utf-8

"""
ID:          issue-1092
ISSUE:       1092
TITLE:       Tricky index names can defeat the parsing logic when generating a human readable plan
DESCRIPTION:
JIRA:        CORE-2508
FBTEST:      bugs.core_2508
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table t(a int not null);
    create index "abc(" on t(a);
    set planonly;
    select * from t where a in (0, 1, 2);
    -- This will produce in 2.5.x:
    -- PLAN (T INDEX (abc(abc(abc())
    --                  ^^^ ^^^
    --                   |   |
    --                   +---+--- NO commas here!
    -- Compare with 3.0:
    -- PLAN (T INDEX (abc(, abc(, abc())
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (T INDEX (abc(, abc(, abc())
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

