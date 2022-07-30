#coding:utf-8

"""
ID:          transactions.read-consist-sttm-restart-on-merge-01
TITLE:       READ CONSISTENCY. Check creation of new statement-level snapshot and restarting changed caused by MERGE. Test-01.
DESCRIPTION:
  Initial article for reading:
      https://asktom.oracle.com/pls/asktom/f?p=100:11:::::P11_QUESTION_ID:11504247549852
      Note on terms which are used there: "BLOCKER", "LONG" and "FIRSTLAST" - their names are slightly changed here
      to: LOCKER-1, WORKER and LOCKER-2 respectively.

      **********************************************

      This test verifies that statement-level snapshot and restart will be performed when "main" session ("worker")
      performs MERGE statement and is involved in update conflicts.
      ("When update conflict is detected <...> then engine <...> creates new statement-level snapshot and restart execution...")

      ::: NB :::
      This test uses script %FBT_REPO%/files/read-consist-sttm-restart-DDL.sql which contains common DDL for all other such tests.
      Particularly, it contains two TRIGGERS (TLOG_WANT and TLOG_DONE) which are used for logging of planned actions and actual
      results against table TEST. These triggers use AUTONOMOUS transactions in order to have ability to see results in any
      outcome of test.

      ###############
      Following scenario if executed here (see also: "doc/README.read_consistency.md"; hereafer is marked as "DOC"):

      * three rows are inserted into the table TEST, with ID = 1,2,3 (and X=1,2,3)
      * session 'locker-1' ("BLOCKER" in Tom Kyte's article ):
              update test set id = id where id = 3;

      * session 'worker' ("LONG" in TK article) has mission:
              merge into test t -- THIS MUST BE LOCKED
              using (select * from test order by id) s on s.id=t.id
              when matched then
                  update set t.id = -t.id, t.x = -s.x
              when not matched then
                  insert(id,x) values(s.id, -s.x - 500);
              -- and it does this within read committed read consistency.


          // Execution will have PLAN ORDER <ASCENDING_INDEX>.
          // Worker starts with updating rows with ID = 1, 2 but can not change row with ID = 3 because of locker-1.
          // Because of detecting update conflist, worker changes here its TIL to RC NO RECORD_VERSION.

      * session 'locker-2' ("FIRSTLAST" in TK article):
              (1) insert into test(id) values(-13);
              (2) commit;
              (3) update test set id=id where id = -13;
          // session-'worker' remains waiting at this point because row with ID = 3 is still occupied by by locker-1.
          // Record with (new) id = -13 will be seen further because worker's TIL was changed to RC NO RECORD_VERSION.

      * session 'locker-1':
              (1) commit;
              (2) insert into test(id) values(-12);
              (3) commit;
              (4) update test set id=id where id = -12;

          // This: '(1) commit' - will release record with ID = 3. Worker sees this record and put write-lock on it.
          // [DOC]: "b) engine put write lock on conflicted record"
          // Because of TIL = RC NRV session-'worker' must see all committed records regardless on its own snapshot.
          // Worker resumes search for rows that must be updated with taking in account required order of its DML (i.e. 'ORDER BY ID').
          // [DOC]: "c) engine continue to evaluate remaining records of update/delete cursor and put write locks on it too"
          // New record which is involved in DML (and did not exist before) *will be found*, its ID = -13.
          // Worker stops on this record (with ID = -13) because id is occupied by locker-2.
          // BECAUSE OF FACT THAT AT LEAST ONE ROW *WAS FOUND* - STATEMENT-LEVEL RESTART *NOT* YET OCCURS HERE.
          // [DOC]: "d) when there is *no more* records to fetch, engine start to undo all actions performed since
          //            top-level statement execution starts and preserve already taken write locks
          //         e) then engine restores transaction isolation mode as READ COMMITTED *READ CONSISTENCY*,
          //            creates new statement-level snapshot and restart execution of top-level statement."

      * session 'locker-2':
              commit;

          // This: 'commit' - will release record with ID = -13. Worker sees this record and put write-lock on it.
          // [DOC]: "b) engine put write lock on conflicted record"
          // Because of TIL = RC NRV session-'worker' must see all committed records regardless on its own snapshot.
          // Worker resumes search for rows that must be updated with taking in account required order of its DML (i.e. 'ORDER BY ID').
          // [DOC]: "c) engine continue to evaluate remaining records of update/delete cursor and put write locks on it too"
          // New record which is involved in DML (and did not exist before) *will be found*, its ID = -12.
          // Worker stops on this record (with ID = -12) because id is occupied by locker-1.
          // BECAUSE OF FACT THAT AT LEAST ONE ROW *WAS FOUND* - STATEMENT-LEVEL RESTART *NOT* YET OCCURS HERE.
          // [DOC]: "d) when there is *no more* records to fetch, engine start to undo all actions performed since
          //            top-level statement execution starts and preserve already taken write locks
          //         e) then engine restores transaction isolation mode as READ COMMITTED *READ CONSISTENCY*,
          //            creates new statement-level snapshot and restart execution of top-level statement."


      * session 'locker-1':
              commit;
          // This commit will release record with ID = -12. Worker sees this record and put write-lock on it.
          // At this point there are no more records to be locked (by worker) that meet cursor condition: worker did put
          // write locks on all rows that meet its cursor conditions.
          // BECAUSE OF FACT THAT NO MORE RECORDS FOUND TO BE LOCKED, WORKER DOES UNDO BUT KEEP LOCKS AND THEN
          // MAKES FIRST STATEMENT-LEVEL RESTART. This restart is also the last in this test.


      Expected result:
      * session-'worker' must update of all rows with reverting signs of their IDs. Records which were inserted must have positive IDs.

      * Two unique values must be in the column TLOG_DONE.SNAP_NO for session-'worker' when it performed MERGE statement: first of them
        was created by initial statement start and second reflects SINGLE restart (this column has values which are evaluated using
        rdb$get_context('SYSTEM', 'SNAPSHOT_NUMBER') -- see trigger TEST_AIUD).
        It is enough to count these values using COUNT(*) or enumarate them by DENSE_RANK() function.

      NOTE: concrete values of fields TRN, GLOBAL_CN and SNAP_NO in the TLOG_DONE can differ from one to another run!
      This is because of concurrent nature of connections that work against database. We must not assume that these values will be constant.

      ################

      NOTE test contains for-loop in order to check different target objects: TABLE ('test') and VIEW ('v_test'), see 'checked_mode'.
FBTEST:      functional.transactions.read_consist_sttm_restart_on_merge_01
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
    checked_mode: table, STDLOG: Records affected: 5

    checked_mode: table, STDLOG:      ID       X
    checked_mode: table, STDLOG: ======= =======
    checked_mode: table, STDLOG:      -3      -3
    checked_mode: table, STDLOG:      -2      -2
    checked_mode: table, STDLOG:      -1      -1
    checked_mode: table, STDLOG:      12      12
    checked_mode: table, STDLOG:      13      13
    checked_mode: table, STDLOG: Records affected: 5

    checked_mode: table, STDLOG:  OLD_ID OP              SNAP_NO_RANK
    checked_mode: table, STDLOG: ======= ====== =====================
    checked_mode: table, STDLOG:       1 UPD                        1
    checked_mode: table, STDLOG:       2 UPD                        1
    checked_mode: table, STDLOG:     -13 UPD                        2
    checked_mode: table, STDLOG:     -12 UPD                        2
    checked_mode: table, STDLOG:       1 UPD                        2
    checked_mode: table, STDLOG:       2 UPD                        2
    checked_mode: table, STDLOG:       3 UPD                        2
    checked_mode: table, STDLOG: Records affected: 7


    checked_mode: view, STDLOG: Records affected: 5

    checked_mode: view, STDLOG:      ID       X
    checked_mode: view, STDLOG: ======= =======
    checked_mode: view, STDLOG:      -3      -3
    checked_mode: view, STDLOG:      -2      -2
    checked_mode: view, STDLOG:      -1      -1
    checked_mode: view, STDLOG:      12      12
    checked_mode: view, STDLOG:      13      13
    checked_mode: view, STDLOG: Records affected: 5

    checked_mode: view, STDLOG:  OLD_ID OP              SNAP_NO_RANK
    checked_mode: view, STDLOG: ======= ====== =====================
    checked_mode: view, STDLOG:       1 UPD                        1
    checked_mode: view, STDLOG:       2 UPD                        1
    checked_mode: view, STDLOG:     -13 UPD                        2
    checked_mode: view, STDLOG:     -12 UPD                        2
    checked_mode: view, STDLOG:       1 UPD                        2
    checked_mode: view, STDLOG:       2 UPD                        2
    checked_mode: view, STDLOG:       3 UPD                        2
    checked_mode: view, STDLOG: Records affected: 7
"""


@pytest.mark.version('>=4.0')
def test_1(act: Action, fn_worker_sql: Path, fn_worker_log: Path, fn_worker_err: Path, capsys):
    sql_init = (act.files_dir / 'read-consist-sttm-restart-DDL.sql').read_text()

    for checked_mode in('table', 'view'):
        target_obj = 'test' if checked_mode == 'table' else 'v_test'

        # add rows with ID = 1, 2, 3:
        sql_addi = f'''
            set term ^;
            execute block as
            begin
                rdb$set_context('USER_SESSION', 'WHO', 'INIT_DATA');
            end
            ^
            set term ;^
            insert into {target_obj}(id, x)
            select row_number()over(),row_number()over()
            from rdb$types rows 3;
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

            con_lock_1.execute_immediate( f'update {target_obj} set id=id where id = 3' )

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

                set list off;
                set wng off;
                set count on;

                merge into {target_obj} t -- THIS MUST BE LOCKED
                using (select * from {target_obj} order by id) s on s.id=t.id
                when matched then
                    update set t.id = -t.id, t.x = -s.x
                when not matched then
                    insert(id,x) values(s.id, -s.x - 500);

                -- check results:
                -- ###############

                select id,x from {target_obj} order by id; -- this will produce output only after all lockers do their commit/rollback

                select v.old_id, v.op, v.snap_no_rank
                from v_worker_log v
                where v.op  = 'upd';

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
                                               '-pag', '9999999',
                                               act.db.dsn
                                            ],
                                              stdout = hang_out,
                                              stderr = hang_err
                                           )
                time.sleep(1)

                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_2.execute_immediate( f'insert into {target_obj}(id,x) values(-13,-13)')
                con_lock_2.commit()
                con_lock_2.execute_immediate( f'update {target_obj} set id=id where id = -13')

                #########################
                ###  L O C K E R - 1  ###
                #########################
                con_lock_1.commit()
                con_lock_1.execute_immediate( f'insert into {target_obj}(id,x) values(-12,-12)' )
                con_lock_1.commit()
                con_lock_1.execute_immediate( f'update {target_obj} set id=id where id = -12' )

                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_2.commit()

                #########################
                ###  L O C K E R - 1  ###
                #########################
                con_lock_1.commit() # WORKER will complete his job after this

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
