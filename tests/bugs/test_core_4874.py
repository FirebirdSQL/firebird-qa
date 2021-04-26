#coding:utf-8
#
# id:           bugs.core_4874
# title:        Infinite "similar to" matching
# decription:   
#                    Confirmed normal work (evaluation for less than 2 ms) on WI-T4.0.0.1598
#                
# tracker_id:   CORE-4874
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;

    set term ^;
    execute block as
    begin
        rdb$set_context( 'USER_SESSION','DTS_START', cast('now' as timestamp) );
        rdb$set_context( 'USER_SESSION','MAX_THRESHOLD_MS',  500 );
        --                                                    ^
        --                                                    |
        --                                      #############################
        --                                      MAX ALLOWED EXECUTION TIME,MS
        --                                      #############################
    end
    ^
    set term ;^

    select 1 from rdb$database 
    where 
    '<tr style="height: 1px"><td width="11"/><td width="17"/><td width="43"/><td width="35"/><td width="30"/><td width="125"/><td width="4"/><td width="49"/><td width="83"/><td width="136"/><td width="117"/><td width="8"/><td width="4"/><td width="53"/><td width="13"/><td width="21"/><td width="7"/></tr>' 
    similar to '%>(_%_){0,6}</td>' escape '\\' 
    --                                     ^
    --                                     |
    --                  ATTENTION: TWO BACKSLASHES MUST BE HERE WHEN USE FBT_RUN TO CHECK
    --                             ###############
    ;

    set count off;
    select 
        iif( evaluated_ms <= max_allowed_ms
            ,'acceptable'
            ,'TOO LONG: ' || evaluated_ms || ' ms - this is more then threshold = ' || max_allowed_ms || ' ms'
           ) as duration
    from (
        select 
             datediff( millisecond from cast(rdb$get_context( 'USER_SESSION','DTS_START') as timestamp) to current_timestamp ) evaluated_ms
            ,cast( rdb$get_context( 'USER_SESSION','MAX_THRESHOLD_MS' ) as int ) as max_allowed_ms
        from rdb$database
    );
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
    DURATION                        acceptable
  """

@pytest.mark.version('>=4.0')
def test_core_4874_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

