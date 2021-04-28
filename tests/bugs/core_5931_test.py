#coding:utf-8
#
# id:           bugs.core_5931
# title:        SIMILAR TO does not return result when invalid pattern is used (with two adjacent special characters that should be escaped but aren't)
# decription:   
#                    Confirmed normal work (evaluation for less than 5 ms) on WI-T4.0.0.1598
#                
# tracker_id:   CORE-5931
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
        rdb$set_context( 'USER_SESSION','MAX_THRESHOLD_MS',  100 );
        --                                                    ^
        --                                                    |
        --                                      #############################
        --                                      MAX ALLOWED EXECUTION TIME,MS
        --                                      #############################
    end
    ^
    set term ;^

    select 1 as result from rdb$database where 
    ' 
    group by 
    f01, 
    f02, 
    f03, 
    f04, 
    f05, 
    f06, 
    f07, 
    f08, 
    f09, 
    f10, 
    f11, 
    f12, 
    f13 
    ' 
        similar to 
    '%group[[:WHITESPACE:]]+by[[:WHITESPACE:]]+([[:ALNUM:]]|_)+([[:WHITESPACE:]]*,[[:WHITESPACE:]]*[[:ALNUM:]]+){12,}[[:WHITESPACE:]]*%' 
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
    RESULT                          1
    Records affected: 1
    DURATION                        acceptable
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

