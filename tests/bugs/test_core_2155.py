#coding:utf-8
#
# id:           bugs.core_2155
# title:        Join of SP with view or table may fail with "No current record for fetch operation"
# decription:   
# tracker_id:   CORE-2155
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;

    select v.rdb$relation_id, p.*
    from v_relations_a v
    INNER join sp_test(v.rdb$field_id) p on 1=1;
    
    select v.rdb$relation_id, p.*
    from v_relations_b v
    INNER join sp_test(v.rdb$field_id) p on 1=1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (V RDB$RELATIONS NATURAL, P NATURAL)
    PLAN JOIN (V DUMMY_ALIAS NATURAL, P NATURAL)
  """

@pytest.mark.version('>=3.0')
def test_core_2155_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

