#coding:utf-8

"""
ID:          transactions.read-consist-sttm-restart-on-delete-03
TITLE:       READ CONSISTENCY. Check creation of new statement-level snapshot and restarting changed caused by DELETE. Test-03.
DESCRIPTION:
  Initial article for reading:
          https://asktom.oracle.com/pls/asktom/f?p=100:11:::::P11_QUESTION_ID:11504247549852
          Note on terms which are used there: "BLOCKER", "LONG" and "FIRSTLAST" - their names are slightly changed here
          to: LOCKER-1, WORKER and LOCKER-2 respectively.
      See also: doc/README.read_consistency.md

      **********************************************

      This test verifies that statement-level snapshot and restart will be performed when "main" session ("worker")
      performs DELETE statement and is involved in update conflicts.
      ("When update conflict is detected <...> then engine <...> creates new statement-level snapshot and restart execution...")

      ::: NB :::
      This test uses script %FBT_REPO%/files/read-consist-sttm-restart-DDL.sql which contains common DDL for all other such tests.
      Particularly, it contains two TRIGGERS (TLOG_WANT and TLOG_DONE) which are used for logging of planned actions and actual
      results against table TEST. These triggers use AUTONOMOUS transactions in order to have ability to see results in any
      outcome of test.

      ###############
      Following scenario if executed here (see also: "doc/README.read_consistency.md"; hereafer is marked as "DOC"):

      * add new table that is child to test: TDETL (with FK that references TEST and 'on delete cascade' clause)
      * three rows are inserted into the table TEST, with IDs: 2, 3 and 5.

      * session 'locker-1' ("BLOCKER" in Tom Kyte's article ):
              update set id=id where id = 5;

      * session 'worker' ("LONG" in TK article) has mission:
              delete from test where id >= 3 order by id; // using TIL = read committed read consistency

          // Execution will have PLAN ORDER <ASCENDING_INDEX>.
          // It will delete (first avaliable for cursor) row with ID = 3 but can not change row with ID = 5 because of locker-1.
          // Update conflict appears here and, because of this, worker temporary changes its TIL to RC no record_version (RC NRV).
          // [DOC]: "a) transaction isolation mode temporarily switched to the READ COMMITTED *NO RECORD VERSION MODE*"
          // This (new) TIL allows worker further to see all committed versions, regardless of its own snapshot.

      * session 'locker-2' ("FIRSTLAST" in TK article): replaces ID = 2 with new value = 4, then commits
        and locks this record again:
              (1) update test set id = 4 where id = 2;
              (2) commit;
              (3) update test set id=id where id = 4;
          // session-'worker' remains waiting at this point because row with ID = 5 is still occupied by by locker-1
          // but worker must further see record with (new) id = 4 because its TIL was changed to RC NO RECORD_VERSION.

      * session 'locker-1':
              (1) commit;
              (2) insert into test(id) values(6);
              (3) insert into detl(id, pid) values(6001, 6);
              (4) commit;
              (5) update test set id=id where id=6;
          // first of these statements: '(1) commit' - will release record with ID = 5.
          // Worker sees this record (because of TIL = RC NRV) and put write-lock on it.
          // [DOC]: "b) engine put write lock on conflicted record"
          // Also, because worker TIL = RC NRV, it will see two new rows with ID = 4 and 6, and they meet worker cursor condition ("id>=3").
          // Worker resumes search for any rows with ID >=3, and it does this with taking in account "ORDER BY ID ASC".
          // [DOC]: "c) engine continue to evaluate remaining records of update/delete cursor and put write locks on it too"
          // Worker starts to search records which must be involved in its DML and *found* sucn rows (with ID = 4 and 6).
          // NB. These rows currently can NOT be deleted by worker because of locker-2 and locker-1 have uncommitted updates.
          // BECAUSE OF FACT THAT AT LEAST ONE ROW *WAS FOUND* - STATEMENT-LEVEL RESTART *NOT* YET OCCURS HERE.
          // :::!! NB, AGAIN !! ::: restart NOT occurs here because at least one records found, see:
          // [DOC]: "d) when there is *no more* records to fetch, engine start to undo all actions performed since
          //            top-level statement execution starts and preserve already taken write locks
          //         e) then engine restores transaction isolation mode as READ COMMITTED *READ CONSISTENCY*,
          //            creates new statement-level snapshot and restart execution of top-level statement."

      * session 'locker-2':
             commit;
          // This will release record with ID = 4 (but row with ID = 6 is still inaccessible because of locker-1).
          // Worker sees record (because of TIL = RC NRV) with ID = 4 and put write-lock on it.
          // Then worker resumes search for any (new) rows with ID >= 3, and it does this with taking in account required order
          // of its DML (i.e. ORDER BY ID ASC).
          // [DOC]: "c) engine continue to evaluate remaining records of update/delete cursor and put write locks on it too"
          // But there are no such rows in the tableL earlier worker already encountered all possible rows (with ID=4 and 6)
          // and *did* put write-locks on them. So at this point NO new rows can be found for putting new lock on it.
          // BECAUSE OF FACT THAT NO RECORDS FOUND, WORKER DOES UNDO BUT KEEP LOCKS AND THEN MAKES FIRST STATEMENT-LEVEL RESTART.
          // [DOC]: "d) when there is no more records to fetch, engine start to undo all actions ... and preserve already taken write locks
          //         e) then engine restores transaction isolation mode as READ COMMITTED *READ CONSISTENCY*,
          //           creates new statement-level snapshot and restart execution of top-level statement."

      * session 'locker-1':
             commit;
          // This will release record with ID = 6 - and this is the last row which meet cursor condition of session-worker.
          // Worker sees record (because of TIL = RC NRV) with ID = 6 and put write-lock on it.
          // Then worker resumes search for any (new) rows with ID >= 3, and it does this with taking in account required order
          // of its DML (i.e. ORDER BY ID ASC). NO new rows (with ID >= 3) can be found for putting new lock on it.
          // BECAUSE OF FACT THAT NO RECORDS FOUND, WORKER DOES UNDO BUT KEEP LOCKS AND THEN MAKES SECOND STATEMENT-LEVEL RESTART.

      Expected result:
      * session-'worker' must *successfully* complete deletion of all rows which it could see at the starting point (ID=3 and 5)
        PLUS rows with ID = 4 (ex. ID=2) and 6  (this ID is new, it did not exist at the statement start).
        As result, all rows must be deleted.

      * three unique values must be in the column TLOG_DONE.SNAP_NO for session-'worker' when it performed DELETE statement: first of them
        was created by initial statement start and all others reflect two restarts (this column has values which are evaluated using
        rdb$get_context('SYSTEM', 'SNAPSHOT_NUMBER') -- see trigger TEST_AIUD).
        It is enough to count these values using COUNT(*) or enumarate them by DENSE_RANK() function.

      NOTE: concrete values of fields TRN, GLOBAL_CN and SNAP_NO in the TLOG_DONE can differ from one to another run!
      This is because of concurrent nature of connections that work against database. We must not assume that these values will be constant.
      ################

FBTEST:      functional.transactions.read_consist_sttm_restart_on_delete_03
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

    checked_mode: table, STDLOG: Records affected: 0

    checked_mode: table, STDLOG:  OLD_ID OP              SNAP_NO_RANK
    checked_mode: table, STDLOG: ======= ====== =====================
    checked_mode: table, STDLOG:       3 DEL                        1
    checked_mode: table, STDLOG:       3 DEL                        2
    checked_mode: table, STDLOG:       3 DEL                        3
    checked_mode: table, STDLOG:       4 DEL                        3
    checked_mode: table, STDLOG:       5 DEL                        3
    checked_mode: table, STDLOG:       6 DEL                        3
    checked_mode: table, STDLOG: Records affected: 6


    checked_mode: view, STDLOG: Records affected: 4

    checked_mode: view, STDLOG: Records affected: 0

    checked_mode: view, STDLOG:  OLD_ID OP              SNAP_NO_RANK
    checked_mode: view, STDLOG: ======= ====== =====================
    checked_mode: view, STDLOG:       3 DEL                        1
    checked_mode: view, STDLOG:       3 DEL                        2
    checked_mode: view, STDLOG:       3 DEL                        3
    checked_mode: view, STDLOG:       4 DEL                        3
    checked_mode: view, STDLOG:       5 DEL                        3
    checked_mode: view, STDLOG:       6 DEL                        3
    checked_mode: view, STDLOG: Records affected: 6
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, fn_worker_sql: Path, fn_worker_log: Path, fn_worker_err: Path, capsys):
    sql_init = (act.files_dir / 'read-consist-sttm-restart-DDL.sql').read_text()

    for checked_mode in('table', 'view'):
        target_obj = 'test' if checked_mode == 'table' else 'v_test'

        sql_addi='''
            recreate table detl(id int, PID int references test on delete cascade on update cascade);
            commit;

            delete from test;
            insert into test(id, x) values(2,2);
            insert into test(id, x) values(3,3);
            insert into test(id, x) values(5,5);
            insert into detl(id, pid) values(2000, 2);
            insert into detl(id, pid) values(2001, 2);
            insert into detl(id, pid) values(2002, 2);
            insert into detl(id, pid) values(3001, 3);
            insert into detl(id, pid) values(5001, 5);
            insert into detl(id, pid) values(5001, 5);
            commit;
        '''

        act.isql(switches=['-q'], input = 'recreate table detl(id int);' ) # drop dependencies
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

            con_lock_1.execute_immediate( f'update {target_obj} set id=id where id = 5' )

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
                SET KEEP_TRAN_PARAMS ON;
                set transaction read committed read consistency;
                --select current_connection, current_transaction from rdb$database;
                set list off;
                set wng off;
                --set plan on;
                set count on;

                delete from {target_obj} where id >= 3 order by id; -- THIS MUST BE LOCKED

                -- check results:
                -- ###############

                select id from {target_obj} order by id; -- this will produce output only after all lockers do their commit/rollback

                select v.old_id, v.op, v.snap_no_rank
                from v_worker_log v
                where v.op = 'del';

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
                                               act.db.dsn
                                            ],
                                              stdout = hang_out,
                                              stderr = hang_err
                                           )
                time.sleep(1)


                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_2.execute_immediate( f'update {target_obj} set id=4 where id=2;' )
                con_lock_2.commit()
                con_lock_2.execute_immediate( f'update {target_obj} set id=id where id=4;' )


                con_lock_1.commit() # release record with ID=5 (allow it to be deleted by session-worker)

                # Add record which did not exists when session-worker statement started.
                # Add also child record for it, then commit + re-lock just added record:
                con_lock_1.execute_immediate( f'insert into {target_obj}(id,x) values(6,6)' )
                con_lock_1.execute_immediate( f'insert into detl(id, pid) values(6001, 6)' )
                con_lock_1.commit()
                con_lock_1.execute_immediate( f'update {target_obj} set id=id where id=6' )

                con_lock_2.commit() # release record with ID=4. At this point session-worker will be allowed to delete rows with ID=4 and 5.

                con_lock_1.commit() # release record with ID=6. It is the last record which also must be deleted by session-worker.

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
