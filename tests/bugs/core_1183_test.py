#coding:utf-8
#
# id:           bugs.core_1183
# title:        View cannot be created if its WHERE clause contains IN <subquery> with a procedure reference
# decription:   
# tracker_id:   CORE-1183
# min_versions: []
# versions:     2.0.2
# qmid:         bugs.core_1183

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.2
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    create or alter procedure p
      returns (col int)
    as
    begin
      col = 1;
      suspend;
    end^
    set term ;^
    commit;
    
    create or alter view v
    as
      select
          rdb$description v_descr,
          rdb$relation_id v_rel_id,
          rdb$character_set_name v_cset_name
      from rdb$database
      where 1 in ( select col from p );
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select v_descr, sign(v_rel_id) as v_rel_id, v_cset_name
    from v;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    V_DESCR                         <null>
    V_REL_ID                        1
    V_CSET_NAME                     NONE                                                                                         
  """

@pytest.mark.version('>=2.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

