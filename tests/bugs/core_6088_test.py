#coding:utf-8
#
# id:           bugs.core_6088
# title:        "SIMILAR TO" hangs when processing parenthesis
# decription:   
#                    Confirmed normal work (evaluation for less than 5 ms) on WI-T4.0.0.1598
#                    31.12.2020: increased max duration threshold from 100 to 150 ms.
#                
# tracker_id:   CORE-6088
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
        rdb$set_context( 'USER_SESSION','MAX_THRESHOLD_MS',  150 );
        --                                                    ^
        --                                                    |
        --                                      #############################
        --                                      MAX ALLOWED EXECUTION TIME,MS
        --                                      #############################
    end
    ^
    set term ;^


    select 1 as result from RDB$DATABASE 
    where 'a-b c(d)' 
    similar to '[[:WHITESPACE:]a-z\\-]{0,199}' escape '\\'
    --                                                ^
    --                                                |
    --                              ATTENTION: TWO BACKSLASHES MUST BE HERE WHEN USE FBT_RUN TO CHECK
    --                                         ###############
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

