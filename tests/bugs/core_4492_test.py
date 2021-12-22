#coding:utf-8
#
# id:           bugs.core_4492
# title:        OR/IN predicates for RDB$DBKEY lead to NATURAL plan
# decription:   
#                    Checked on:
#                       30SS, build 3.0.3.32856: OK, 1.156s.
#                       40SS, build 4.0.0.834: OK, 1.109s.
#               
#                    Following query will not compile:
#                      select 1 from rdb$relations a join rdb$relations b using ( rdb$db_key );
#                      Statement failed, SQLSTATE = 42000 / -Token unknown /  -rdb$db_key ==> Why ?
#               
#                    Sent letter to dimitr, 25.11.2017 22:42. Waiting for reply.
#                    27.12.2017: seems that this note will remain unresolved for undef. time.
#                
# tracker_id:   CORE-4492
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (RDB$RELATIONS INDEX ())
    PLAN JOIN (A NATURAL, B INDEX ())
    PLAN (V RDB$RELATIONS INDEX (), V RDB$RELATIONS INDEX ())
    PLAN HASH (B RDB$RELATIONS NATURAL, B RDB$RELATIONS NATURAL, A RDB$RELATIONS NATURAL, A RDB$RELATIONS NATURAL)
    PLAN (RDB$RELATIONS INDEX ())
"""

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

