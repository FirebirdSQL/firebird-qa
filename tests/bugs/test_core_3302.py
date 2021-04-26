#coding:utf-8
#
# id:           bugs.core_3302
# title:        Distinct aggregates return wrong (duplicated) data
# decription:   Note: LIST() does not guarantee that returned values will be sorted so we can only count words in the resulting string and compare it with checked count
# tracker_id:   CORE-3302
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t( dt date);
    commit;
    insert into t values( '2011-01-07' );
    insert into t values( '2011-01-07' ); 
    insert into t values( '2011-01-07' ); 
    insert into t values( '2011-01-06' );
    insert into t values( '2011-01-06' );
    insert into t values( '2011-01-06' );
    insert into t values( '2011-01-08' );
    insert into t values( '2011-01-08' );
    insert into t values( '2011-01-08' );
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select char_length(s)-char_length(replace(s,',',''))+1 words_cnt, check_cnt
    from (
    select
       list(distinct 
              case extract(weekday from dt) 
                   when 0 then 'Sun' when 1 then 'Mon' when 2 then 'Tue' 
                   when 3 then 'Wed' when 4 then 'Thu' when 5 then 'Fri' 
                   when 6 then 'Sat' end
           ) s
       ,count(distinct dt) check_cnt
    from t
    )
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WORDS_CNT                       3
    CHECK_CNT                       3  
  """

@pytest.mark.version('>=2.5.1')
def test_core_3302_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

