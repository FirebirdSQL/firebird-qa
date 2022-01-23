#coding:utf-8

"""
ID:          issue-1566
ISSUE:       1566
TITLE:       OR/IN predicates for RDB$DBKEY lead to NATURAL plan
DESCRIPTION:
NOTES:
[25.11.2017]
  Following query will not compile:
    select 1 from rdb$relations a join rdb$relations b using ( rdb$db_key );
    Statement failed, SQLSTATE = 42000 / -Token unknown /  -rdb$db_key ==> Why ?

  Sent letter to dimitr, 25.11.2017 22:42. Waiting for reply.
[27.12.2017] seems that this note will remain unresolved for undef. time.
JIRA:        CORE-4492
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;

    recreate view v_unioned as
    select rdb$relation_id as rel_id, rdb$db_key as db_key from rdb$relations
    union all
    select rdb$relation_id, rdb$db_key from rdb$relations
    ;

    set planonly;
    --set echo on;

    select 1 from rdb$relations where rdb$db_key in (?, ?);
    select 2 from rdb$relations a join rdb$relations b on a.rdb$db_key = b.rdb$db_key;
    select 3 from v_unioned v where v.db_key in (?, ?);
    select 4 from v_unioned a join v_unioned b on a.db_key = b.db_key;

    -- 27.12.2017: this works fine (fixed by dimitr, see letter 01.12.2017 09:57):
    select 5 from rdb$relations where rdb$db_key is not distinct from ?;

"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (RDB$RELATIONS INDEX ())
    PLAN JOIN (A NATURAL, B INDEX ())
    PLAN (V RDB$RELATIONS INDEX (), V RDB$RELATIONS INDEX ())
    PLAN HASH (B RDB$RELATIONS NATURAL, B RDB$RELATIONS NATURAL, A RDB$RELATIONS NATURAL, A RDB$RELATIONS NATURAL)
    PLAN (RDB$RELATIONS INDEX ())
"""

@pytest.mark.version('>=3.0.3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

