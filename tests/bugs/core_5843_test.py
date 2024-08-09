#coding:utf-8

"""
ID:          issue-6104
ISSUE:       6104
TITLE:       Wrong handling of failures of TRANSACTION START trigger
DESCRIPTION:
JIRA:        CORE-5843
FBTEST:      bugs.core_5843
NOTES:
    [25.11.2023] pzotov
    Writing code requires more care since 6.0.0.150: ISQL does not allow specifying duplicate delimiters without any statements between them (two semicolon, two carets etc).
"""

import pytest
from firebird.qa import *

substitutions = [('line[:]{0,1}[\\s]+[\\d]+.*', 'line'),
                 ('transaction[\\s]+[\\d]+[\\s]+aborted', 'transaction aborted'),
                 ('tx=[\\d]+', 'tx='), ('TX_ID[\\s]+[\\d]+', 'TX_ID'),
                 ('exception[\\s]+[\\d]+.*', 'exception')]

init_script = """
    --set echo on;
    set bail on;
    create or alter trigger tx_rollback on transaction rollback as begin end;
    create or alter trigger tx_start on transaction start as begin end;
    create or alter trigger tx_commit on transaction commit as begin end;

    create or alter view v_mon as
    select
        t.mon$transaction_id as tx_id
        ,t.mon$state as tx_state
        --,a.mon$remote_process att_process
        --,a.mon$attachment_name as att_name
        --,a.mon$system_flag as att_sysflag
        --,a.mon$user as att_user
    from mon$transactions t
    join mon$attachments a using (mon$attachment_id)
    where mon$attachment_id = current_connection
    ;
    commit;

    set term ^;

    create or alter exception ex_tra_start 'transaction @1 aborted'
    ^

    create or alter procedure tx_trig_log(msg varchar(255))
    as
    declare s varchar(255);
    begin
        s = rdb$get_context('USER_SESSION', 'tx_trig_log');
        if (s <> '') then
        begin
            s = s || ASCII_CHAR(10) || trim(msg) || ', current tx=' || current_transaction;
            rdb$set_context('USER_SESSION', 'tx_trig_log', :s);
        end
    end
    ^

    create or alter trigger tx_start on transaction start as
    declare s varchar(255);
    begin
        execute procedure tx_trig_log('trigger on transaction start ');

        if (rdb$get_context('USER_SESSION', 'tx_abort') = 1) then
        begin
            execute procedure tx_trig_log('exception on tx start ');
            rdb$set_context('USER_SESSION', 'tx_abort', 0);
            exception ex_tra_start using (current_transaction);
        end
    end
    ^

    create or alter trigger tx_commit on transaction commit as
        declare s varchar(255);
    begin
        execute procedure tx_trig_log('trigger on commit');
    end
    ^

    create or alter trigger tx_rollback on transaction rollback as
        declare s varchar(255);
    begin
        execute procedure tx_trig_log('trigger on rollback');
    end
    ^

    create or alter procedure sp_use_atx as
    begin
        rdb$set_context('USER_SESSION', 'tx_abort', 1);
        execute procedure tx_trig_log('sp_use_atx, point_a');
        in autonomous transaction do
            execute procedure tx_trig_log('sp_use_atx, point_b');
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set autoddl off;
    set list on;
    commit;

    select 'test_1, point-1' as msg, v.* from rdb$database cross join v_mon v;

    set term ^;
    execute block as
        declare c int;
    begin
        c = rdb$set_context('USER_SESSION', 'tx_abort', 1); -- flag to raise error on next tx start
    end
    ^
    set term ;^
    commit;

    select 'test_1, point-2' as msg, v.* from rdb$database cross join v_mon v; -- it start transaction
    commit;

    set count on;
    select 'test_1, point-3' as msg, v.* from rdb$database cross join v_mon v;
    set count off;
    rollback;

    -------------------------------------------------------------

    --connect '$(DSN)' user 'SYSDBA' password 'masterkey';

    set term ^;
    execute block as
        declare c int;
    begin
        c = rdb$set_context('USER_SESSION', 'tx_trig_log', ascii_char(10) || 'start: tx=' || current_transaction ); -- start logging
    end
    ^
    set term ;^
    commit;

    select 'test2, point-a' as msg, v.* from rdb$database cross join v_mon v;

    execute procedure sp_use_atx;

    /*
        Statement failed, SQLSTATE = HY000
        exception 3
        -EX_TRA_START
        -transaction 692 aborted
        -At trigger 'TX_START' line: 10, col: 5
        At procedure 'sp_use_atx' line: 4, col: 3
    */

    select rdb$get_context('USER_SESSION', 'tx_trig_log') from rdb$database;

"""

act = isql_act('db', test_script, substitutions=substitutions)

expected_stdout = """
    MSG                             test_1, point-1
    TX_ID                           22
    TX_STATE                        1

    MSG                             test_1, point-3
    TX_ID                           25
    TX_STATE                        1
    Records affected: 1

    MSG                             test2, point-a
    TX_ID                           28
    TX_STATE                        1
    RDB$GET_CONTEXT
    start: tx=26
    trigger on commit, current tx=26
    trigger on transaction start, current tx=28
    sp_use_atx, point_a, current tx=28
    trigger on transaction start, current tx=29
    exception on tx start, current tx=29

"""

expected_stderr = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_TRA_START
    -transaction 23 aborted
    -At trigger 'TX_START' line

    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_TRA_START
    -transaction 29 aborted
    -At trigger 'TX_START' line
    At procedure 'SP_USE_ATX' line
"""

@pytest.mark.version('>=3.0.4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
