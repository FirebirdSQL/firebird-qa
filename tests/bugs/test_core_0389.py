#coding:utf-8
#
# id:           bugs.core_0389
# title:        NULLS FIRST does not work with unions
# decription:   
# tracker_id:   CORE-389
# min_versions: ['2.0.7']
# versions:     2.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """
    create table t(x int);
    insert into t values(2222);
    insert into t values(222 );
    insert into t values(22);
    insert into t values(2);
    insert into t values(null);
    insert into t values(null);
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    select distinct x
    from t
    
    union all
    
    select distinct x
    from t
    
    order by 1 nulls first
    ;
    --------------------------
    select distinct x
    from t
    
    union all
    
    select distinct x
    from t
    
    order by 1 desc nulls first
    ;
    --------------------------
    select x
    from t

    union

    select x
    from t

    order by 1 nulls first
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
               X 
    ============ 
          <null> 
          <null> 
               2 
               2 
              22 
              22 
             222 
             222 
            2222 
            2222 
    
    
               X 
    ============ 
          <null> 
          <null> 
            2222 
            2222 
             222 
             222 
              22 
              22 
               2 
               2 

               X 
    ============ 
          <null> 
               2 
              22 
             222 
            2222
  """

@pytest.mark.version('>=2.0.7')
def test_core_0389_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

