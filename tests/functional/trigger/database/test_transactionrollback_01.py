#coding:utf-8
#
# id:           functional.trigger.database.transactionrollback_01
# title:        Trigger on rollback transaction
# decription:   
#                   Test trigger on rollback transaction
#                   Checked 17.05.2017 on:
#                       FB25Cs, build 2.5.8.27056: OK, 1.047ss.
#                       FB25SC, build 2.5.8.27061: OK, 0.516ss.
#                       fb25sS, build 2.5.7.27038: OK, 0.719ss.
#                       fb30Cs, build 3.0.3.32721: OK, 2.516ss.
#                       fb30SC, build 3.0.3.32721: OK, 1.297ss.
#                       FB30SS, build 3.0.3.32721: OK, 1.578ss.
#                       FB40CS, build 4.0.0.639: OK, 2.656ss.
#                       FB40SC, build 4.0.0.639: OK, 1.844ss.
#                       FB40SS, build 4.0.0.639: OK, 1.735ss.
#                
# tracker_id:   CORE-645
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         functional.trigger.database.transactionrollback_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    create sequence g;
    commit;

    create view v_check as 
    select rdb$get_context('USER_SESSION', 'TRG_TX') as ctx 
    from rdb$database;
    commit;

    set term ^;
    create or alter trigger trg_tx_rbak inactive on transaction rollback position 0 as
    begin
      --- nop ---
    end 
    ^
    set term ;^
    commit;

    recreate table test(id int);
    commit;

    recreate table log (main_app_tx int,  db_trigger_tx int default current_transaction, add_info varchar(80) );
    commit;

    set term ^;
    create or alter trigger trg_tx_rbak inactive on transaction rollback position 0 as
    begin
        rdb$set_context('USER_SESSION', 'TRG_TX', gen_id(g,1));
    end 
    ^
    set term ;^
    commit;

    set autoddl off;
    alter trigger trg_tx_rbak active;
    commit;

    select gen_id(g,0) as curr_g, v.* from v_check v; -- 0, <null>

    rollback; -- this should increase value of sequence 'g' by 1 and assign new value to context var. 'TRG_TX' 

    set transaction no wait;
    select gen_id(g,0) as curr_g, v.* from v_check v; -- 1, 1 (the same! becase Tx START should not be watched by trg_tx_rbak)

    commit;                                           
    select gen_id(g,0) as curr_g, v.* from v_check v; -- 1, 1 (the same! because COMMIT should not be watched by trg_tx_rbak)

    set term ^;
    create or alter trigger trg_tx_rbak active on transaction rollback position 0 as
    begin
        rdb$set_context('USER_SESSION', 'TRG_TX', gen_id(g,1234)/0);
    end 
    ^
    set term ;^
    commit;

    -- this should increase value of sequence 'g' by 1234 but context var. 'TRG_TX' 
    -- will store old value because of zero-divide exception
    rollback;

    -- NB: client should NOT get exception (zero divide) from trigger which is defined for __ROLLBACK__ event!

    select gen_id(g,0) as curr_g, v.* from v_check v; -- 1235, 1
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CURR_G                          0
    CTX                             <null>

    CURR_G                          1
    CTX                             1

    CURR_G                          1
    CTX                             1

    CURR_G                          1235
    CTX                             1
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

