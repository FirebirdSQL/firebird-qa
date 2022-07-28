#coding:utf-8

"""
ID:          transactions.read-consist-statement-delete-undone-02
TITLE:       READ CONSISTENCY. Changes produced by DELETE statement must be UNDONE when cursor resultset becomes empty after this statement start. Test-02
DESCRIPTION:
  Initial article for reading:
          https://asktom.oracle.com/pls/asktom/f?p=100:11:::::P11_QUESTION_ID:11504247549852
          Note on terms which are used there: "BLOCKER", "LONG" and "FIRSTLAST" - their names are slightly changed here
          to: LOCKER-1, WORKER and LOCKER-2 respectively.
      See also: doc/README.read_consistency.md

      **********************************************

      ::: NB :::
      This test uses script %FBT_REPO%/files/read-consist-sttm-restart-DDL.sql which contains common DDL for all other such tests.
      Particularly, it contains two TRIGGERS (TLOG_WANT and TLOG_DONE) which are used for logging of planned actions and actual
      results against table TEST. These triggers launched AUTONOMOUS transactions in order to have ability to see results in any
      outcome of test.

      ###############
      Following scenario if executed here:
      * five rows are inserted into the table TEST, with IDs: 1...5.

      * session 'locker-1' ("BLOCKER" in Tom Kyte's article ):
              update test set id = id where id = 1;

      * session 'worker' ("LONG" in TK article) has mission:
              delete from test where x not in (select x from test where id >= 4) order by id desc;  // using TIL = read committed read consistency

          // Execution will have PLAN ORDER <DESCENDING_INDEX>.
          // It will delete rows starting with ID = 5 and down to ID = 2, but hang on row with ID = 1 because of locker-1;

      * session 'locker-2' ("FIRSTLAST" in TK article):
              (1) insert into test(id) values(-1);
              (2) commit;
              (3) update test set id=id where id = -1;

          // session-'worker' remains waiting at this point because row with ID = 1 is still occupied by by locker-1
          // but worker must further see record with (new) id = -1 because its TIL was changed to RC NO RECORD_VERSION.

      * session 'locker-1':
              (1) commit;
              (2) insert into test(id) values(-2);
              (3) commit;
              (4) update test set id=id where id = -2;

          // This: '(1) commit' - will release record with ID = 1. Worker sees this record and put write-lock on it.
          // [DOC]: "b) engine put write lock on conflicted record"
          // Because of TIL = RC NRV session-'worker' must see all committed records regardless on its own snapshot.
          // Worker resumes search for any rows which with taking in account required order of its DML (i.e. 'ORDER BY ID DESC').
          // [DOC]: "c) engine continue to evaluate remaining records of update/delete cursor and put write locks on it too"
          // Worker starts to search records which must be involved in its DML and *found* row that was not yet locked: it has ID = 1.
          // Then it goes on and stops on ID = -1 because id is occupied by locker-2.
          // BECAUSE OF FACT THAT AT LEAST ONE ROW *WAS FOUND* - STATEMENT-LEVEL RESTART *NOT* YET OCCURS HERE.
          // [DOC]: "d) when there is *no more* records to fetch, engine start to undo all actions performed since
          //            top-level statement execution starts and preserve already taken write locks
          //         e) then engine restores transaction isolation mode as READ COMMITTED *READ CONSISTENCY*,
          //            creates new statement-level snapshot and restart execution of top-level statement."

      * session 'locker-2':
              (1) commit;
              (2) insert into test(id, x) values(10, NULL); -- ::: NB ::: X is NULL here!
              (3) update test set id=id where id = 10;

          // This: '(1) commit' - will release record with ID = -1. Worker sees this record and put write-lock on it.
          // [DOC]: "b) engine put write lock on conflicted record"
          // Because of TIL = RC NRV session-'worker' must see all committed records regardless on its own snapshot.
          // Worker resumes search for any rows which with taking in account required order of its DML (i.e. 'ORDER BY ID DESC').
          // [DOC]: "c) engine continue to evaluate remaining records of update/delete cursor and put write locks on it too"
          // Worker starts to search records which must be involved in its DML and *found* row that was not yet locked: it has ID = -1.
          // Then it goes on and stops on ID = -2 because id is occupied by locker-1.
          // BECAUSE OF FACT THAT AT LEAST ONE ROW *WAS FOUND* - STATEMENT-LEVEL RESTART *NOT* YET OCCURS HERE.
          // [DOC]: "d) when there is *no more* records to fetch, engine start to undo all actions performed since
          //            top-level statement execution starts and preserve already taken write locks
          //         e) then engine restores transaction isolation mode as READ COMMITTED *READ CONSISTENCY*,
          //            creates new statement-level snapshot and restart execution of top-level statement."
          // ::: NB :::
          // Expression  "where x not in (select x from test where id >= 4)" will be evaluated as FALSE since this point
          // because one of its records has NULL in 'X' column.

      * session 'locker-1':
              commit;

          // this allows session-worker to delete row with ID = -2.
          // session-worker must immediately cancel its DML because now it sees record with ID = 10 and X is NULL which not meets NOT-IN requirements.

      Expected result:
      * session-'worker' must be cancelled. No rows must be deleted, PLUS new rows must remain (with ID = -1, -2 and 10).
      * we must NOT see statement-level restart because no rows actually were affected by session-worker statement.
        Column TLOG_DONE.SNAP_NO must contain only one unique value that relates to start of DELETE statement.
      ################

      Checked on 4.0.0.2151 SS/CS
FBTEST:      functional.transactions.read_consist_statement_delete_undone_02
NOTES:
[28.07.2022] pzotov
    Checked on 4.0.1.2692, 5.0.0.591
"""

import subprocess
import pytest
from firebird.qa import *
from pathlib import Path

db = db_factory()

act = python_act('db', substitutions=[('=', ''), ('[ \t]+', ' ')])

fn_worker_sql = temp_file('tmp_worker.sql')
fn_worker_log = temp_file('tmp_worker.log')
fn_worker_err = temp_file('tmp_worker.err')

expected_stdout = """
    Records affected: 0

         ID
    =======
         -2
         -1
          1
          2
          3
          4
          5
         10

    Records affected: 8

     OLD_ID OP              SNAP_NO_RANK
    ======= ====== =====================
          3 DEL                        1
          2 DEL                        1

    Records affected: 2
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, fn_worker_sql: Path, fn_worker_log: Path, fn_worker_err: Path, capsys):
    sql_init = (act.files_dir / 'read-consist-sttm-restart-DDL.sql').read_text()

    # add rows with ID = 1,2,3,4,5:
    sql_addi='''
        set term ^;
        execute block as
        begin
            rdb$set_context('USER_SESSION', 'WHO', 'INIT_DATA');
        end
        ^
        set term ;^
        insert into test(id, x)
        select row_number()over(),row_number()over()
        from rdb$types rows 5;
        commit;
    '''
    act.isql(switches=['-q'], input = ''.join( (sql_init, sql_addi) ) )

    with act.db.connect() as con_lock_1, act.db.connect() as con_lock_2:
        for i,c in enumerate((con_lock_1,con_lock_2)):
            sttm = f"execute block as begin rdb$set_context('USER_SESSION', 'WHO', 'LOCKER #{i+1}'); end"
            c.execute_immediate(sttm)

        #########################
        ###  L O C K E R - 1  ###
        #########################
        con_lock_1.execute_immediate( 'update test set id=id where id = 1' )

        worker_sql = '''
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

            delete from test where x not in (select x from test where id >= 4) order by id desc; -- THIS MUST BE LOCKED

            -- check results:
            -- ###############


            select id from test order by id; -- this will produce output only after all lockers do their commit/rollback

            select v.old_id, v.op, v.snap_no_rank
            from v_worker_log v
            where v.op = 'del';

            set width who 10;
            -- DO NOT check this! Values can differ here from one run to another!
            --select id, trn, who, old_id, new_id, op, rec_vers, global_cn, snap_no from tlog_done order by id;

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
            con_lock_2.execute_immediate( 'insert into test(id,x) values( -1, -1 )')
            con_lock_2.commit()
            con_lock_2.execute_immediate( 'update test set id=id where id=-1' )

            #########################
            ###  L O C K E R - 1  ###
            #########################
            con_lock_1.commit() # releases record with ID=1 (allow it to be deleted by session-worker)
            con_lock_1.execute_immediate( 'insert into test(id, x) values(-2, -2);' )
            con_lock_1.commit()
            con_lock_1.execute_immediate( 'update test set id = id where id = -2' )


            #########################
            ###  L O C K E R - 2  ###
            #########################
            con_lock_2.commit()
            con_lock_2.execute_immediate( 'insert into test(id, x) values(10, null)' )
            con_lock_2.commit()

            #########################
            ###  L O C K E R - 1  ###
            #########################
            con_lock_1.commit() # <<< THIS MUST CANCEL ALL PERFORMED DELETIONS OF SESSION-WORKER

            # Here we wait until ISQL complete its mission:
            p_worker.wait()

    for g in (fn_worker_log, fn_worker_err):
        with g.open() as f:
            print( f.read() )

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
