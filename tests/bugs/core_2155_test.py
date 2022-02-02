#coding:utf-8

"""
ID:          issue-2586
ISSUE:       2586
TITLE:       Join of SP with view or table may fail with "No current record for fetch operation"
DESCRIPTION:
JIRA:        CORE-2155
FBTEST:      bugs.core_2155
"""

import pytest
from firebird.qa import *

init_script = """
    set term ^;
    create or alter procedure sp_test(a_id int) returns (a_dup int) as
    begin
        a_dup = 2*a_id;
        suspend;
    end
    ^
    set term ;^

    create or alter view v_relations_a as
    select rdb$relation_id, rdb$field_id
    from rdb$relations;

    create or alter view v_relations_b as
    select dummy_alias.rdb$relation_id, dummy_alias.rdb$field_id
    from rdb$relations as dummy_alias;
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set planonly;

    select v.rdb$relation_id, p.*
    from v_relations_a v
    INNER join sp_test(v.rdb$field_id) p on 1=1;

    select v.rdb$relation_id, p.*
    from v_relations_b v
    INNER join sp_test(v.rdb$field_id) p on 1=1;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN JOIN (V RDB$RELATIONS NATURAL, P NATURAL)
    PLAN JOIN (V DUMMY_ALIAS NATURAL, P NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

