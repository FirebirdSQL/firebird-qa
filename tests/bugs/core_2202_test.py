#coding:utf-8
#
# id:           bugs.core_2202
# title:        RDB$VIEW_RELATIONS is not cleaned when altering a view
# decription:   
# tracker_id:   CORE-2202
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table table_1 (id integer);
    recreate table table_2 (id integer);
    recreate table table_3 (id integer);
    
    create or alter view vw_table(id) as
    select id from table_1;
    commit;
    
    create or alter view vw_table(id) as
    select id from table_2;
    commit;
    
    create or alter view vw_table(id) as
    select id
    from table_3;
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set width vew_name 31;
    set width rel_name 31;
    set width ctx_name 31;
    select
         rdb$view_name as vew_name
        ,rdb$relation_name as rel_name
        ,rdb$view_context
        ,rdb$context_name as ctx_name
    from rdb$view_relations rv;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    VEW_NAME                        VW_TABLE                                                                                     
    REL_NAME                        TABLE_3                                                                                      
    RDB$VIEW_CONTEXT                1
    CTX_NAME                        TABLE_3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
  """

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

