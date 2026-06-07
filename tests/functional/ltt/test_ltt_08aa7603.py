#coding:utf-8

"""
ID:          n/a
ISSUE:       https://groups.google.com/g/firebird-devel/c/8vlKSNckyuw/m/BTSkzb6wAQAJ
TITLE:       LTT with index. Crash when DDL + DML are in the same Tx and 'COMMIT' presents between 'DROP INDEX' and 'DROP TABLE'.
DESCRIPTION:
NOTES:
    [07.06.2026] pzotov
    Discission:
        https://groups.google.com/g/firebird-devel/c/8vlKSNckyuw/m/BTSkzb6wAQAJ
    Fixed in:
        https://github.com/FirebirdSQL/firebird/commit/08aa760318e64c211d443351b0e453976d214577
    Confirmed bug on 6.0.0.1996-263e09.
    Checked on 6.0.0.1999-c8bc46b.
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'
test_sql = f"""
    set bail on;
    set heading off;
    set autoddl off;
    commit;

    recreate LOCAL TEMPORARY table test(f01 int) on commit DELETE rows;
    commit;
    insert into test(f01) select i from generate_series(1, 1000) as s(i);

    create index test_idx on test(f01);
    drop index test_idx;

    commit; ----------------------- [ ! ]

    drop table test;
    commit;

    select '{COMPLETED_MSG}' as msg from rdb$database;
"""

db = db_factory()
act = isql_act('db', test_sql)

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = f"""
        {COMPLETED_MSG}
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
