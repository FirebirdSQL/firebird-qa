#coding:utf-8
#
# id:           bugs.core_5664
# title:        SIMILAR TO is substantially (500-700x) slower than LIKE on trivial pattern matches with VARCHAR data.
# decription:   
#                    Confirmed normal work (ratio is about 1) on WI-T4.0.0.1598
#                
# tracker_id:   CORE-5664
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
    set bail on; 
    set term ^; 


    -- test#1: <long_string> SIMILAR TO '%QWERTY'
    --         ##################################

    execute block returns(
        ratio_in_test_1 varchar(255)
    ) as 
        declare i int = 0; 
        declare t0 timestamp; 
        declare t1 timestamp; 
        declare elap_ms_using_like int;
        declare elap_ms_using_similar_to int;
        declare s varchar(32761); 
        declare ratio_similar_vs_like numeric(15,4);
        declare MAX_RATIO numeric(15,4) = 2;
        --            ^
        --      #############
        --      MAX THRESHOLD
        --      #############
        declare n_count int = 5000; -- do not set it to values less than 500: duration should not be zero!
    begin 
        s = lpad('', 32755, uuid_to_char(gen_uuid())) || 'QWERTY'; 

        t0 = cast('now' as timestamp); 
        while (i < n_count) do 
        begin 
            i = i + iif( s like '%QWERTY', 1, 1); 
        end 
        t1 = cast('now' as timestamp); 
        elap_ms_using_like = datediff(millisecond from t0 to t1); 

        i = 0; 
        while (i < n_count) do 
        begin 
            i = i + iif( s similar to '%QWERTY', 1, 1); 
        end 
        elap_ms_using_similar_to = datediff(millisecond from t1 to cast('now' as timestamp)); 

        ratio_similar_vs_like = 1.0000 * elap_ms_using_similar_to / elap_ms_using_like;

        ratio_in_test_1 = iif( ratio_similar_vs_like < MAX_RATIO
                        ,'acceptable'
                        ,'TOO LOG: '|| ratio_similar_vs_like ||' times. This is more than max threshold = ' || MAX_RATIO || ' times'
                      )
        ;
        suspend; 
    end
    ^ 


    -- test#2: <long_string> SIMILAR TO 'QWERTY%'
    --         ##################################

    execute block returns(
        ratio_in_test_2 varchar(255)
    ) as 
        declare i int = 0; 
        declare t0 timestamp; 
        declare t1 timestamp; 
        declare elap_ms_using_like int;
        declare elap_ms_using_similar_to int;
        declare s varchar(32761); 
        declare ratio_similar_vs_like numeric(15,4);
        declare MAX_RATIO numeric(15,4) = 2;
        --            ^
        --      #############
        --      MAX THRESHOLD
        --      #############
        declare n_count int = 5000; -- do not set it to values less than 500: duration should not be zero!
    begin 

        s = 'QWERTY' || lpad('', 32755, uuid_to_char(gen_uuid())) ; 

        t0 = cast('now' as timestamp); 
        while (i < n_count) do 
        begin 
            i = i + iif( s similar to 'QWERTY%', 1, 1); 
        end 
        t1 = cast('now' as timestamp); 
        elap_ms_using_like = datediff(millisecond from t0 to t1); 

        i = 0; 
        while (i < n_count) do 
        begin 
            i = i + iif( s similar to 'QWERTY%', 1, 1); 
        end 
        elap_ms_using_similar_to = datediff(millisecond from t1 to cast('now' as timestamp)); 

        ratio_similar_vs_like = 1.0000 * elap_ms_using_similar_to / elap_ms_using_like;

        ratio_in_test_2 = iif( ratio_similar_vs_like < MAX_RATIO
                        ,'acceptable'
                        ,'TOO LONG: '|| ratio_similar_vs_like ||' times. This is more than max threshold = ' || MAX_RATIO || ' times'
                      )
        ;
        suspend; 
    end
    ^ 
    set term ;^ 

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RATIO_IN_TEST_1                 acceptable
    RATIO_IN_TEST_2                 acceptable
  """

@pytest.mark.version('>=4.0')
def test_core_5664_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

