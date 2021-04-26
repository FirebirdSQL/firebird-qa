#coding:utf-8
#
# id:           bugs.core_5542_db_attach
# title:        Database-level triggers related to TRANSACTION events (i.e. start, commit and rollback) do not take in account their POSITION index (when more than one trigger for the same event type is defined)
# decription:   
#                   Note. This test does check only for 'DATABASE CONNECT' case (though it worked Ok before this bug was found).
#                   Resuls for 22.05.2017:
#                       fb30Cs, build 3.0.3.32725: OK, 2.203ss.
#                       fb30SC, build 3.0.3.32725: OK, 1.375ss.
#                       FB30SS, build 3.0.3.32725: OK, 1.328ss.
#                       FB40CS, build 4.0.0.645: OK, 2.391ss.
#                       FB40SC, build 4.0.0.645: OK, 1.422ss.
#                       FB40SS, build 4.0.0.645: OK, 2.375ss.
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
    create or alter trigger trg_db_attach_beta inactive on connect position 0 as begin end
    ^
    create or alter trigger trg_db_attach_anna inactive on connect position 0 as begin end
    ^
    create or alter trigger trg_db_attach_ciao inactive on connect position 0 as begin end
    ^
    commit
    ^
    drop trigger trg_db_attach_beta
    ^
    drop trigger trg_db_attach_anna
    ^
    drop trigger trg_db_attach_ciao
    ^

    recreate table tsignal( id integer )
    ^
    recreate table trg_log( id integer, msg varchar(20) );
    ^

    execute block as
    begin
        execute statement 'drop sequence g';
        when any do begin end
    end
    ^
    set term ;^
    commit;

    set autoddl off;
    set bail on;

    create sequence g;
    commit;

    set term ^;
    create trigger trg_log_bi for trg_log active before insert position 0 as
    begin
        new.id = coalesce( new.id, gen_id(g,1) );
    end 
    ^
    set term ;^
    commit;

    ------------------------------------------------------------------------

    set term ^;
    create or alter trigger trg_db_attach_ciao active on connect position 111 as
    begin
        if ( exists(select * from tsignal) ) then
            insert into trg_log(msg) values('trigger tx_ciao');
    end 
    ^

    create or alter trigger trg_db_attach_anna active on connect position 22 as
    begin
        if ( exists(select * from tsignal) ) then
            insert into trg_log(msg) values('trigger tx_anna');
    end 
    ^

    create or alter trigger trg_db_attach_beta active on connect position 3 as
    begin
        if ( exists(select * from tsignal) ) then
            insert into trg_log(msg) values('trigger tx_beta');
    end 
    ^
    
    set term ;^
    commit;

    insert into tsignal(id) values(1);
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
 
    select
         r.rdb$trigger_name             
        ,r.rdb$trigger_sequence
        ,r.rdb$trigger_type
    from rdb$triggers r
    where r.rdb$trigger_name starting with upper('TRG_DB_ATTACH')
    order by r.rdb$trigger_sequence
    ;

    set count on;
    select * from trg_log;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$TRIGGER_NAME                TRG_DB_ATTACH_BETA
    RDB$TRIGGER_SEQUENCE            3
    RDB$TRIGGER_TYPE                8192
    RDB$TRIGGER_NAME                TRG_DB_ATTACH_ANNA
    RDB$TRIGGER_SEQUENCE            22
    RDB$TRIGGER_TYPE                8192
    RDB$TRIGGER_NAME                TRG_DB_ATTACH_CIAO
    RDB$TRIGGER_SEQUENCE            111
    RDB$TRIGGER_TYPE                8192
    ID                              1
    MSG                             trigger tx_beta
    ID                              2
    MSG                             trigger tx_anna
    ID                              3
    MSG                             trigger tx_ciao
    Records affected: 3
  """

@pytest.mark.version('>=3.0')
def test_core_5542_db_attach_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

