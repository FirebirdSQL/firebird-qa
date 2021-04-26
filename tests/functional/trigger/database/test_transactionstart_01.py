#coding:utf-8
#
# id:           functional.trigger.database.transactionstart_01
# title:        Trigger on start tansaction
# decription:   
#                   This tests normal operation of database TRANSACTION START trigger.
#               
#                   Checked 17.05.2017 on:
#                   FB25Cs, build 2.5.8.27056: OK, 1.375ss.
#                   FB25SC, build 2.5.8.27061: OK, 0.407ss.
#                   fb25sS, build 2.5.7.27038: OK, 0.953ss.
#                   fb30Cs, build 3.0.3.32721: OK, 2.937ss.
#                   fb30SC, build 3.0.3.32721: OK, 1.906ss.
#                   FB30SS, build 3.0.3.32721: OK, 1.125ss.
#                   FB40CS, build 4.0.0.639: OK, 3.422ss.
#                   FB40SC, build 4.0.0.639: OK, 1.859ss.
#                   FB40SS, build 4.0.0.639: OK, 1.266ss.
#               
#                
# tracker_id:   CORE-745
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         functional.trigger.database.transactionstart_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('line: \\d+, col: \\d+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set autoddl off;
    create table trg_log(id integer, trg_tx int default current_transaction);

    create view v_check as
    select count(*) as cnt_chk_tx, count(iif(trg_tx=current_transaction,1,null)) as cnt_chk_trg
    from trg_log 
    where trg_tx = current_transaction;

    set term ^;
    create trigger trg_start_tx inactive on transaction start position 0 as
    begin
        insert into trg_log default values;
        --insert into trg_log(trg_tx) values (current_transaction);
    end 
    ^
    set term ;^
    commit;

    alter trigger trg_start_tx active;
    commit;

    set list on;
    set autoddl off;

    select 'Tx to be rolled back' as phase
           --, current_transaction 
    from rdb$database;
    --select a.* from trg_log a;
    select * from v_check;
    rollback;


    select 'Tx to be committed' as phase
           --, current_transaction 
    from rdb$database;
    --select a.* from trg_log a;
    select * from v_check;
    commit;

    select 'Final select' as phase
           --, current_transaction 
    from rdb$database;
    --select a.* from trg_log a order by id desc rows 1;
    select * from v_check;

    set term ^;
    alter trigger trg_start_tx inactive position 0 as
    begin
        insert into trg_log(trg_tx) values (1/0);
    end 
    ^
    set term ;^
    commit;

    alter trigger trg_start_tx active;
    commit;

    commit; -- this should raise exception in trg_start_tx and this exception SHOULD PASS to the client.
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PHASE                           Tx to be rolled back
    CNT_CHK_TX                      1
    CNT_CHK_TRG                     1
    PHASE                           Tx to be committed
    CNT_CHK_TX                      1
    CNT_CHK_TRG                     1
    PHASE                           Final select
    CNT_CHK_TX                      1
    CNT_CHK_TRG                     1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
    -At trigger 'TRG_START_TX'
  """

@pytest.mark.version('>=3.0')
def test_transactionstart_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

