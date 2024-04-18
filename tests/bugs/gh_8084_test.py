#coding:utf-8

"""
ID:          issue-8084
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8084
TITLE:       Partial index uniqueness violation
DESCRIPTION:
NOTES:
    [18.04.2024] pzotov
    Confirmed bug on 6.0.0.315
    Checked on 6.0.0.321 #1d96c10 - all OK.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    recreate table test (
      id bigint primary key
      ,a bigint not null
      ,b smallint not null
    );

    create unique index idx_test_a on test(a) where (b = 1);

    insert into test(id, a, b) values (1, 1, 0);
    insert into test(id, a, b) values (2, 2, 1);
    commit;

    insert into test(id, a, b) values (3, 1, 0); -- must pass
    commit;
    insert into test(id, a, b) values (4, 2, 1); -- must fail with "attempt to store duplicate value"
    rollback;

    update test set b = 1 where id = 1; -- must pass
    commit;

    update test set b = 1 where id = 3; -- BUG was here: passed before fix but must fail.
    commit;

    select a+0 as a, count(*) as a_cnt from test where b+0 = 1 group by a+0;
"""

act = isql_act('db', test_script, substitutions=[('[ \t]+', ' ')])

expected_stdout = """
    Statement failed, SQLSTATE = 23000
    attempt to store duplicate value (visible to active transactions) in unique index "IDX_TEST_A"
    -Problematic key value is ("A" = 2)

    Statement failed, SQLSTATE = 23000
    attempt to store duplicate value (visible to active transactions) in unique index "IDX_TEST_A"
    -Problematic key value is ("A" = 1)

    A 1
    A_CNT 1

    A 2
    A_CNT 1
"""

@pytest.mark.version('>=6.0.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
