#coding:utf-8

"""
ID:          transactions.read-consist-sttm-restart-on-update-02
TITLE:       READ CONSISTENCY. Check creation of new statement-level snapshot and restarting changed caused by UPDATE. Test-02.
DESCRIPTION:
  Initial article for reading:
      https://asktom.oracle.com/pls/asktom/f?p=100:11:::::P11_QUESTION_ID:11504247549852
      Note on terms which are used there: "BLOCKER", "LONG" and "FIRSTLAST" - their names are slightly changed here
      to: LOCKER-1, WORKER and LOCKER-2 respectively.

      **********************************************

      This test verifies that statement-level snapshot and restart will be performed when "main" session ("worker")
      performs UPDATE statement and is involved in update conflicts.
      ("When update conflict is detected <...> then engine <...> creates new statement-level snapshot and restart execution...")

      ::: NB :::
      This test uses script %FBT_REPO%/files/read-consist-sttm-restart-DDL.sql which contains common DDL for all other such tests.
      Particularly, it contains two TRIGGERS (TLOG_WANT and TLOG_DONE) which are used for logging of planned actions and actual
      results against table TEST. These triggers use AUTONOMOUS transactions in order to have ability to see results in any
      outcome of test.

      ###############
      Following scenario if executed here (see also: "doc/README.read_consistency.md"; hereafer is marked as "DOC"):

      * five rows are inserted into the table TEST, with IDs: 1,2,3,4,5
      * session 'locker-1' ("BLOCKER" in Tom Kyte's article ):
              delete from test where id = 5;

      * session 'worker' ("LONG" in TK article) has mission:
              update test set id = -id where exists(select * from test where id < 0 or id = 5) order by id; // using TIL = read committed read consistency

          // Execution will have PLAN ORDER <ASCENDING_INDEX>.
          // Worker starts with updating rows with ID = 1...4 but can not change row with ID = 5 because of locker-1.
          // Because of detecting update conflist, worker changes here its TIL to RC NO RECORD_VERSION.

      * session 'locker-2' ("FIRSTLAST" in TK article):
              (1) insert into test(id) values(-11);
              (2) commit;
              (3) delete from test where id = -11;

          // session-'worker' remains waiting at this point because row with ID = 5 is still occupied by by locker-1.
          // Record with (new) id = -11 will be seen further because worker's TIL was changed to RC NO RECORD_VERSION.

      * session 'locker-1':
              (1) commit;
              (2) insert into test(id) values(-12);
              (3) commit;
              (4) delete from test where id = -12;

          // This: '(1) commit' - removes record with id = 5.
          // Because of TIL = RC NRV session-'worker' must see all committed records regardless on its own snapshot.
          // Thus worker sees record with id = -11 (which is locked now by locker-2) and puts write-lock on it.
          // [DOC]: "b) engine put write lock on conflicted record"
          // BECAUSE OF FACT THAT AT LEAST ONE ROW *WAS FOUND* - STATEMENT-LEVEL RESTART *NOT* YET OCCURS HERE.
          // [DOC]: "d) when there is *no more* records to fetch, engine start to undo all actions performed since
          //            top-level statement execution starts and preserve already taken write locks
          //         e) then engine restores transaction isolation mode as READ COMMITTED *READ CONSISTENCY*,
          //            creates new statement-level snapshot and restart execution of top-level statement."

      * session 'locker-2':
              (1) commit;
              (2) insert into test(id) values(-13);
              (3) commit;
              (4) update test set id=id where id = -13;

          // This: '(1) commit' - removes record with id = -11.
          // Because of TIL = RC NRV session-'worker' must see all committed records regardless on its own snapshot.
          // Thus worker sees record with id = -12 (which is locked now by locker-1) and puts write-lock on it.
          // BECAUSE OF FACT THAT AT LEAST ONE ROW *WAS FOUND* - STATEMENT-LEVEL RESTART *NOT* YET OCCURS HERE.

      * session 'locker-1':
              (1) commit;
              (2) insert into test(id) values(-14);
              (3) commit;
              (4) update test set id=id where id = -14;

          // This: '(1) commit' - removes record with id = -12.
          // Because of TIL = RC NRV session-'worker' must see all committed records regardless on its own snapshot.
          // Thus worker sees record with id = -13 (which is locked now by locker-2) and puts write-lock on it.
          // BECAUSE OF FACT THAT AT LEAST ONE ROW *WAS FOUND* - STATEMENT-LEVEL RESTART *NOT* YET OCCURS HERE.

      * session 'locker-2':
              (1) commit;

          // This removes record with id = -13.
          // Worker still waits for record with id = -14 which is occupied by locker-1.

      * session 'locker-1':
              (1) commit;

          // This removes record with id = -14.
          // At this point there are no more records to be locked (by worker) that meet cursor condition: worker did put
          // write locks on all rows that meet its cursor conditions.
          // BECAUSE OF FACT THAT NO MORE RECORDS FOUND TO BE LOCKED, WORKER DOES UNDO BUT KEEP LOCKS AND THEN
          // MAKES FIRST STATEMENT-LEVEL RESTART. This restart is also the last in this test.


      Expected result:
      * session-'worker' must update of only rows with ID = 1...4 (reverting sign of IDs value).

      * Two unique values must be in the column TLOG_DONE.SNAP_NO for session-'worker' when it performed UPDATE statement: first of them
        was created by initial statement start and second reflects SINGLE restart (this column has values which are evaluated using
        rdb$get_context('SYSTEM', 'SNAPSHOT_NUMBER') -- see trigger TEST_AIUD).
        It is enough to count these values using COUNT(*) or enumarate them by DENSE_RANK() function.

      NOTE: concrete values of fields TRN, GLOBAL_CN and SNAP_NO in the TLOG_DONE can differ from one to another run!
      This is because of concurrent nature of connections that work against database. We must not assume that these values will be constant.

      ################

      Checked on 4.0.0.2195
      26.09.2020: added for-loop in order to check different target objects: TABLE ('test') and VIEW ('v_test'), see 'checked_mode'.
FBTEST:      functional.transactions.read_consist_sttm_restart_on_update_02
NOTES:
[29.07.2022] pzotov
    Checked on 4.0.1.2692, 5.0.0.591
"""

import subprocess
import pytest
from firebird.qa import *
from pathlib import Path
import time

db = db_factory()

act = python_act('db', substitutions=[('=', ''), ('[ \t]+', ' ')])

fn_worker_sql = temp_file('tmp_worker.sql')
fn_worker_log = temp_file('tmp_worker.log')
fn_worker_err = temp_file('tmp_worker.err')

expected_stdout = """
    checked_mode: table, STDLOG: Records affected: 4

    checked_mode: table, STDLOG:      ID
    checked_mode: table, STDLOG: =======
    checked_mode: table, STDLOG:      -4
    checked_mode: table, STDLOG:      -3
    checked_mode: table, STDLOG:      -2
    checked_mode: table, STDLOG:      -1
    checked_mode: table, STDLOG: Records affected: 4

    checked_mode: table, STDLOG:  OLD_ID OP              SNAP_NO_RANK
    checked_mode: table, STDLOG: ======= ====== =====================
    checked_mode: table, STDLOG:       1 UPD                        1
    checked_mode: table, STDLOG:       2 UPD                        1
    checked_mode: table, STDLOG:       3 UPD                        1
    checked_mode: table, STDLOG:       4 UPD                        1
    checked_mode: table, STDLOG:       1 UPD                        2
    checked_mode: table, STDLOG:       2 UPD                        2
    checked_mode: table, STDLOG:       3 UPD                        2
    checked_mode: table, STDLOG:       4 UPD                        2
    checked_mode: table, STDLOG: Records affected: 8



    checked_mode: view, STDLOG: Records affected: 4

    checked_mode: view, STDLOG:      ID
    checked_mode: view, STDLOG: =======
    checked_mode: view, STDLOG:      -4
    checked_mode: view, STDLOG:      -3
    checked_mode: view, STDLOG:      -2
    checked_mode: view, STDLOG:      -1
    checked_mode: view, STDLOG: Records affected: 4

    checked_mode: view, STDLOG:  OLD_ID OP              SNAP_NO_RANK
    checked_mode: view, STDLOG: ======= ====== =====================
    checked_mode: view, STDLOG:       1 UPD                        1
    checked_mode: view, STDLOG:       2 UPD                        1
    checked_mode: view, STDLOG:       3 UPD                        1
    checked_mode: view, STDLOG:       4 UPD                        1
    checked_mode: view, STDLOG:       1 UPD                        2
    checked_mode: view, STDLOG:       2 UPD                        2
    checked_mode: view, STDLOG:       3 UPD                        2
    checked_mode: view, STDLOG:       4 UPD                        2
    checked_mode: view, STDLOG: Records affected: 8
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, fn_worker_sql: Path, fn_worker_log: Path, fn_worker_err: Path, capsys):
    sql_init = (act.files_dir / 'read-consist-sttm-restart-DDL.sql').read_text()

    for checked_mode in('table', 'view'):
        target_obj = 'test' if checked_mode == 'table' else 'v_test'

        # add rows with ID = 1, 2, ..., 5:
        sql_addi = f'''
            set term ^;
            execute block as
            begin
                rdb$set_context('USER_SESSION', 'WHO', 'INIT_DATA');
            end
            ^
            set term ;^
            insert into {target_obj}(id, x) select row_number()over(),row_number()over() from rdb$types rows 5;
            commit;
        '''

        act.isql(switches=['-q'], input = ''.join( (sql_init, sql_addi) ) )
        # ::: NOTE ::: We have to immediately quit if any error raised in prepare phase.
        # See also letter from dimitr, 01-feb-2022 14:46
        assert act.stderr == ''
        act.reset()

        with act.db.connect() as con_lock_1, act.db.connect() as con_lock_2:
            for i,c in enumerate((con_lock_1,con_lock_2)):
                sttm = f"execute block as begin rdb$set_context('USER_SESSION', 'WHO', 'LOCKER #{i+1}'); end"
                c.execute_immediate(sttm)

            #########################
            ###  L O C K E R - 1  ###
            #########################

            con_lock_1.execute_immediate( f'delete from {target_obj} where id = 5' )

            worker_sql = f'''
                set list on;
                set autoddl off;
                set term ^;
                execute block returns (whoami varchar(30)) as
                begin
                    whoami = 'WORKER'; -- , ATT#' || current_connection;
                    rdb$set_context('USER_SESSION','WHO', whoami);
                    -- suspend;
                end
                ^
                set term ;^
                commit;
                --set echo on;
                SET KEEP_TRAN_PARAMS ON;
                set transaction read committed read consistency;
                --select current_connection, current_transaction from rdb$database;
                set list off;
                set wng off;
                --set plan on;
                set count on;

                update {target_obj} set id = -id order by id; -- THIS MUST BE LOCKED

                -- check results:
                -- ###############

                select id from {target_obj} order by id; -- this will produce output only after all lockers do their commit/rollback

                select v.old_id, v.op, v.snap_no_rank from v_worker_log v where v.op = 'upd';

                set width who 10;
                -- DO NOT check this! Values can differ here from one run to another!
                -- select id, trn, who, old_id, new_id, op, rec_vers, global_cn, snap_no from tlog_done order by id;

                rollback;

            '''

            fn_worker_sql.write_text(worker_sql)

            with fn_worker_log.open(mode='w') as hang_out, fn_worker_err.open(mode='w') as hang_err:

                ############################################################################
                ###  L A U N C H     W O R K E R    U S I N G     I S Q L,   A S Y N C.  ###
                ############################################################################
                p_worker = subprocess.Popen([act.vars['isql'], '-i', str(fn_worker_sql),
                                               '-user', act.db.user,
                                               '-password', act.db.password,
                                               '-pag', '999999',
                                               act.db.dsn
                                            ],
                                              stdout = hang_out,
                                              stderr = hang_err
                                           )
                time.sleep(1)

                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_2.execute_immediate( f'insert into {target_obj}(id) values(-11)' )
                con_lock_2.commit()
                con_lock_2.execute_immediate( f'delete from {target_obj} where id = -11' )

                #########################
                ###  L O C K E R - 1  ###
                #########################
                con_lock_1.commit()
                con_lock_1.execute_immediate( f'insert into {target_obj}(id) values(-12)' )
                con_lock_1.commit()
                con_lock_1.execute_immediate( f'delete from {target_obj} where id = -12' )


                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_2.commit()
                con_lock_2.execute_immediate( f'insert into {target_obj}(id) values(-13)' )
                con_lock_2.commit()
                con_lock_2.execute_immediate( f'delete from {target_obj} where id = -13' )

                #########################
                ###  L O C K E R - 1  ###
                #########################
                con_lock_1.commit()
                con_lock_1.execute_immediate( f'insert into {target_obj}(id) values(-14)' )
                con_lock_1.commit()
                con_lock_1.execute_immediate( f'delete from {target_obj} where id = -14' )

                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_1.commit()

                #########################
                ###  L O C K E R - 1  ###
                #########################
                con_lock_2.commit() # WORKER will complete his job after this


                # Here we wait for ISQL complete its mission:
                p_worker.wait()


        for g in (fn_worker_log, fn_worker_err):
            with g.open() as f:
                for line in f:
                    if line.split():
                        if g == fn_worker_log:
                            print(f'checked_mode: {checked_mode}, STDLOG: {line}')
                        else:
                            print(f'UNEXPECTED STDERR {line}')

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
