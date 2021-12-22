#coding:utf-8
#
# id:           bugs.core_3858
# title:        Very poor performance of SIMILAR TO on some arguments + unable to disconnect via DELETE FROM MON$ATTACHMENTS
# decription:   
#                    Confirmed normal work (evaluation for less than 2 ms) on WI-T4.0.0.1598
#                    Note. Part of pattern: "[[:ALNUM:]\\_\\-]" -- looks strange but it is correct. 
#                    And it should NOT be changed to somewhat like "[[:ALNUM:]]\\_\\-": previoud FB versions hanged exactly 
#                    because of this "strange and wrong" pattern.
#                
# tracker_id:   CORE-3858
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

    select 1 as result from rdb$database where 
    ' 
    group by 
    MATCODE, 
    MATNAME, 
    NOTE, 
    GROUPCODE, 
    STATE, 
    MATPROD, 
    MATFULL, 
    KOLVO, 
    EDIZM, 
    MATGRPCOD, 
    CODE, 
    TEXTTOHIST, 
    INV_ROOMDOC, 
    INV_ROOM, 
    PARENTCODE, 
    INVIS 
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
    assert act_1.clean_stdout == act_1.clean_expected_stdout

