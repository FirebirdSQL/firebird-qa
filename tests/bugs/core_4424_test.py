#coding:utf-8
#
# id:           bugs.core_4424
# title:        Rollback to wrong savepoint if several exception handlers on the same level are executed
# decription:   
#                  Checked on WI-T4.0.0.331.
#                
# tracker_id:   CORE-4424
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
    recreate table test (f_value int);
    recreate table err_log(f_value int, code_point varchar(100));
    commit;

    set term ^;
    create trigger test_aiu for test after update or insert as
        declare a int;
    begin
        if ( new.f_value >= 10 ) then a = 1/0;
    end
    ^
    set term ;^
    commit;

    insert into test values (1);
    commit;

    set term ^;
    execute block as
        declare a int;
        declare g int;
        declare s varchar(100);
    begin
        update test set f_value=2;
        begin
            update test set f_value=3;
            begin
                update test set f_value=4;
                begin
                    update test set f_value=5;
                    begin
                        update test set f_value=6;
                        begin
                            update test set f_value=10;
                        -- NO 'when' here! Exception should pass to upper blobk with 'set f_value=6'
                        end
                    -- NO 'when' here! Exception should pass to upper blobk with 'set f_value=5'
                    end
                -- NO 'when' here! Exception should pass to upper blobk with 'set f_value=4'
                end
            -- At this point:
            -- 1) table 'test' must contain f_value = 4
            -- 2) we just get exception from most nested level.
            -- Now we must log which 'when' sections was in use for handling exception.
            -- Also, we want to check that exception *INSIDE* last 'when' section will be also handled.
            when gdscode arith_except do
                begin
                    s = 'Fall in point_A: "WHEN GDS ARITH"';
                    rdb$set_context('USER_SESSION', s, 'gds='||gdscode );
                    insert into err_log (f_value, code_point) 
                    select f_value, :s || ', gdscode='||gdscode 
                    from test;
                end
            when sqlcode -802 do
                begin
                    s = 'Fall in point_B: "WHEN SQLCODE ' ||sqlcode  || '"';
                    rdb$set_context('USER_SESSION', s, 'gds='||gdscode );
                    insert into err_log (f_value, code_point) 
                    select f_value, :s || ', gdscode='||gdscode 
                    from test;
                end
            when any do
                begin
                    s = 'Fall in point_C: "WHEN ANY", 1st (inner)';
                    rdb$set_context('USER_SESSION', s, 'gds='||gdscode );
                    insert into err_log (f_value, code_point) 
                    select f_value, :s || ', gdscode='||gdscode 
                    from test;
                end
            when any do
                begin
                    
                    rdb$set_context('USER_SESSION','Fall in point_D: "WHEN ANY", 2nd (inner)', 'gds='||gdscode );
                   
                    a = 1/0; -- ###  :::  !!!  NB !!!  :::   ###  EXCEPTION WILL BE HERE!
                    
                    -- NB:
                    -- Previous statement should raise anothernew exception 
                    -- which will force engine to UNDO test.f_value from 4 to 3.
                    -- FB 3.0 will NOT do this (checked on WI-V3.0.1.32575), FB 4.0 works fine.
                end
            end
        when any do
            begin
                s = 'Fall in point_E: "WHEN ANY", final (outer)';
                rdb$set_context('USER_SESSION', s, 'gds='||gdscode  );
                insert into err_log (f_value, code_point) 
                select f_value, :s || ', gds='||gdscode 
                from test;
            end
        end
    end
    ^
    set term ;^
    commit;
    set list on;

    set width ctx_name 40;
    set width ctx_val 15;


    select f_value from test;

    select f_value, code_point from err_log;

    select mon$variable_name as ctx_name, mon$variable_value as ctx_val 
    from mon$context_variables c 
    where c.mon$attachment_id = current_connection;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F_VALUE                         3



    F_VALUE                         3
    CODE_POINT                      Fall in point_E: "WHEN ANY", final (outer), gds=335544321



    CTX_NAME                        Fall in point_A: "WHEN GDS ARITH"
    CTX_VAL                         gds=335544321

    CTX_NAME                        Fall in point_C: "WHEN ANY", 1st (inner)
    CTX_VAL                         gds=0

    CTX_NAME                        Fall in point_D: "WHEN ANY", 2nd (inner)
    CTX_VAL                         gds=0

    CTX_NAME                        Fall in point_E: "WHEN ANY", final (outer)
    CTX_VAL                         gds=335544321
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

