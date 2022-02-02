#coding:utf-8

"""
ID:          issue-4458
ISSUE:       4458
TITLE:       Error when processing an empty data set by window function, if reading indexed
DESCRIPTION:
JIRA:        CORE-4131
FBTEST:      bugs.core_4131
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(x char(31) character set unicode_fss unique using index test_x);
    commit;
    insert into test values('qwerty');
    commit;

    set list on;
    set plan on;
    select row_number() over(order by x) as rn, x
    from test
    where x = 'qwerty'
    ;
    -- 3.0.0.30472:
    -- cursor identified in the UPDATE or DELETE statement is not positioned on a row. no current record for fetch operation
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN SORT (TEST INDEX (TEST_X))
    RN                              1
    X                               qwerty
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

