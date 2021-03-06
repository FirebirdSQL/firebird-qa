#coding:utf-8
#
# id:           bugs.core_5542_tx_commit
# title:        Database-level triggers related to TRANSACTION events (i.e. start, commit and rollback) do not take in account their POSITION index (when more than one trigger for the same event type is defined)
# decription:   
#                   Note. This test does check only for 'TRANSACTION COMMIT' case.
#                   Resuls for 22.05.2017:
#                       fb30Cs, build 3.0.3.32725: OK, 2.281ss.
#                       fb30SC, build 3.0.3.32725: OK, 1.265ss.
#                       FB30SS, build 3.0.3.32725: OK, 1.172ss.
#                       FB40CS, build 4.0.0.645: OK, 2.187ss.
#                       FB40SC, build 4.0.0.645: OK, 1.297ss.
#                       FB40SS, build 4.0.0.645: OK, 1.390ss.
#                
# tracker_id:   CORE-5542
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    set term ^;
    create or alter trigger trg_tx_commit_beta inactive on transaction commit position 0 as begin end
    ^
    create or alter trigger trg_tx_commit_anna inactive on transaction commit position 0 as begin end
    ^
    create or alter trigger trg_tx_commit_ciao inactive on transaction commit position 0 as begin end
    ^
    commit
    ^
    drop trigger trg_tx_commit_beta
    ^
    drop trigger trg_tx_commit_anna
    ^
    drop trigger trg_tx_commit_ciao
    ^

    execute block as
    begin
        execute statement 'drop sequence g';
        when any do begin end
    end
    ^
    set term ;^
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';

    set autoddl off;
    set bail on;

    create sequence g;
    commit;


    set term ^;
    create or alter trigger trg_tx_commit_ciao active on transaction commit position 111 as
        declare c int;
    begin
        if ( rdb$get_context('USER_SESSION','RUN_DB_LEVEL_TRG') is not null ) then
        begin
            --select count(*) from rdb$types,rdb$types,(select 1 i from rdb$types rows 3) into c;
            rdb$set_context('USER_SESSION','RUN_DB_LEVEL_TRG_CIAO', gen_id(g,1) || ': TRG_TX_COMMIT_CIAO ');
        end
    end 
    ^

    create or alter trigger trg_tx_commit_anna active on transaction commit position 3 as
        declare c int;
    begin
        if ( rdb$get_context('USER_SESSION','RUN_DB_LEVEL_TRG') is not null ) then
        begin
            --select count(*) from rdb$types,rdb$types,(select 1 i from rdb$types rows 3) into c;
            rdb$set_context('USER_SESSION','RUN_DB_LEVEL_TRG_ANNA', gen_id(g,1) || ': TRG_TX_COMMIT_ANNA ');
        end
    end 
    ^

    create or alter trigger trg_tx_commit_beta active on transaction commit position 22 as
        declare c int;
    begin
        if ( rdb$get_context('USER_SESSION','RUN_DB_LEVEL_TRG') is not null ) then
        begin
            --select count(*) from rdb$types,rdb$types,(select 1 i from rdb$types rows 3) into c;
            rdb$set_context('USER_SESSION','RUN_DB_LEVEL_TRG_BETA', gen_id(g,1) || ': TRG_TX_COMMIT_BETA ');
        end
    end 
    ^
    
    set term ;^
    commit;

    -- Check (preview):
    select
         r.rdb$trigger_name             
        ,r.rdb$trigger_sequence
        ,r.rdb$trigger_type
    from rdb$triggers r
    where r.rdb$trigger_name starting with upper('trg_tx_commit')
    order by r.rdb$trigger_sequence
    ;


    set term ^;
    execute block as
    begin
      rdb$set_context('USER_SESSION','RUN_DB_LEVEL_TRG', 1); -- Allow triggers to assign values to corresp. context variables 'RUN_DB_LEVEL_TRG_*'
    end
    ^
    set term ;^

    
    set count on;
    commit;

    select 
        c.MON$VARIABLE_NAME
       ,c.MON$VARIABLE_VALUE
    from mon$context_variables c
    where c.mon$attachment_id = current_connection and c.mon$variable_name similar to '%(ANNA|BETA|CIAO)'
    order by c.mon$variable_VALUE
    ;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$TRIGGER_NAME                TRG_TX_COMMIT_ANNA
    RDB$TRIGGER_SEQUENCE            3
    RDB$TRIGGER_TYPE                8195
    RDB$TRIGGER_NAME                TRG_TX_COMMIT_BETA
    RDB$TRIGGER_SEQUENCE            22
    RDB$TRIGGER_TYPE                8195
    RDB$TRIGGER_NAME                TRG_TX_COMMIT_CIAO
    RDB$TRIGGER_SEQUENCE            111
    RDB$TRIGGER_TYPE                8195
    MON$VARIABLE_NAME               RUN_DB_LEVEL_TRG_ANNA
    MON$VARIABLE_VALUE              1: TRG_TX_COMMIT_ANNA
    MON$VARIABLE_NAME               RUN_DB_LEVEL_TRG_BETA
    MON$VARIABLE_VALUE              2: TRG_TX_COMMIT_BETA
    MON$VARIABLE_NAME               RUN_DB_LEVEL_TRG_CIAO
    MON$VARIABLE_VALUE              3: TRG_TX_COMMIT_CIAO
    Records affected: 3
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

