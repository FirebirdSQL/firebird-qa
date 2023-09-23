#coding:utf-8

"""
ID:          transactions.read-consist-sttm-merge-deny-multiple-matches
TITLE:       READ CONSISTENCY. MERGE must reject multiple matches, regardless on statement-level restart.
DESCRIPTION:
  Initial article for reading:
      https://asktom.oracle.com/pls/asktom/f?p=100:11:::::P11_QUESTION_ID:11504247549852
      Note on terms which are used there: "BLOCKER", "LONG" and "FIRSTLAST" - their names are slightly changed here
      to: LOCKER-1, WORKER and LOCKER-2 respectively.

      See also: doc/README.read_consistency.md
      Letter from Vlad: 15.09.2020 20:04 // subj "read consistency // addi test(s)"

      ::: NB :::
      This test uses script %FBT_REPO%/files/read-consist-sttm-restart-DDL.sql which contains common DDL for all other such tests.
      Particularly, it contains two TRIGGERS (TLOG_WANT and TLOG_DONE) which are used for logging of planned actions and actual
      results against table TEST. These triggers use AUTONOMOUS transactions in order to have ability to see results in any
      outcome of test.

      Test verifies DENIAL of multiple matches when MERGE encounteres them, but this statement works in read committed read consistency TIL
      and forced to do several statement-level restarts before such condition will occur.

      Scenario:
      * add initial data to the table TEST: six rows with ID and X = (0, ..., 5);
      * launch LOCKER-1 and catch record with ID = 0: update, then commit and once again update this record (without commit);
      * launch WORKER which tries to do:
            merge into test t
                using (
                    select s.id, s.x from test as s
                    where s.id <= 1
                    order by s.id DESC
                ) s
                on abs(t.id) = abs(s.id)
            when matched then
                update set t.x = t.x * s.x
            ;
        This statement will update record with ID = 1 but then hanging because rows with ID = 0 is locked by LOCKER-1.
        At this point WORKER changes its TIL to RC NO RECORD_VERSION. This allows WORKER to see all records which will be committed later;
        NOTE: records with ID = 2...5 will not be subect for this statement (because they will not returned by data source marked as 's').

      * LOCKER-2 updates row with ID = 5 by reverting sign of this field (i.e. set ID to -5), then issues commit and updates this row again (without commit);
      * LOCKER-1 updates row with ID = 4 and set ID to -4, then issues commit and updates this row again (without commit);
      * LOCKER-2 updates row with ID = 3 and set ID to -3, then issues commit and updates this row again (without commit);
      * LOCKER-1 updates row with ID = 2 and set ID to -2, then issues commit and updates this row again (without commit);
      * LOCKER-2 inserts row (ID,X) = (-1, 1), commit and updates this row again (without commit);
      * LOCKER-1 issues commit;
      * LOCKER-2 issues commit;

      Each of updates/inserts which are performed by LOCKERs lead to new record be appeared in the data source 's' of MERGE statement.
      But note that last statement: insert into test(id,x) values(-1,1) -- creates record that will match TWISE when ON-expression of MERGE
      will evaluates "abs(t.id) = abs(s.id)": first match will be found for record with ID = +1 and second - for newly added rows with ID=-1.

      At this point MERGE must fail with message
          Statement failed, SQLSTATE = 21000
          Multiple source records cannot match the same target during MERGE

      All changes that was performed by MERGE must be rolled back.
      ISQL which did MERGE must issue "Records affected: 2" because MERGE was actually could process records with ID = 1 and 0 (and failed on row with ID=-1).

      Above mentioned actions are performed two times: first for TABLE and second for naturally-updatable VIEW (v_test), see 'target_object_type'.

      Checked on 4.0.0.2214 SS/CS.
FBTEST:      functional.transactions.read_consist_sttm_merge_deny_multiple_matches
NOTES:
    [29.07.2022] pzotov
        Checked on 4.0.1.2692, 5.0.0.591
    [23.09.2023] pzotov
        Replaced verification method of worker attachment presense (which tries DML and waits for resource).
        This attachment is created by *asynchronously* launched ISQL thus using of time.sleep(1) is COMPLETELY wrong.
        Loop with query to mon$statements is used instead (we search for record which SQL_TEXT contains 'special tag', see variable SQL_TAG_THAT_WE_WAITING_FOR).
        Maximal duration of this loop is limited by variable 'MAX_WAIT_FOR_WORKER_START_MS'.
        Many thanks to Vlad for suggestions.

        Checked on WI-T6.0.0.48, WI-T5.0.0.1211, WI-V4.0.4.2988.

"""

import subprocess
import pytest
from firebird.qa import *
from pathlib import Path
import time
import datetime as py_dt

db = db_factory()

act = python_act('db', substitutions=[('=', ''), ('[ \t]+', ' '), ('After line .*', 'After line')])

MAX_WAIT_FOR_WORKER_START_MS = 10000;
SQL_TAG_THAT_WE_WAITING_FOR = 'SQL_TAG_THAT_WE_WAITING_FOR'
# SQL_TO_BE_RESTARTED -- will be defined inside loop, see below!

fn_worker_sql = temp_file('tmp_worker.sql')
fn_worker_log = temp_file('tmp_worker.log')
fn_worker_err = temp_file('tmp_worker.err')

expected_stdout = """
    checked_mode: table, STDLOG: Records affected: 2

    checked_mode: table, STDLOG:      ID       X
    checked_mode: table, STDLOG: ======= =======
    checked_mode: table, STDLOG:      -5       5
    checked_mode: table, STDLOG:      -4       4
    checked_mode: table, STDLOG:      -3       3
    checked_mode: table, STDLOG:      -2       2
    checked_mode: table, STDLOG:      -1       1
    checked_mode: table, STDLOG:       0       0
    checked_mode: table, STDLOG:       1       1

    checked_mode: table, STDLOG: Records affected: 7

    checked_mode: table, STDLOG:  OLD_ID OP              SNAP_NO_RANK
    checked_mode: table, STDLOG: ======= ====== =====================
    checked_mode: table, STDLOG:       0 UPD                        1
    checked_mode: table, STDLOG:       1 UPD                        1
    checked_mode: table, STDLOG:       0 UPD                        2
    checked_mode: table, STDLOG:       1 UPD                        2
    checked_mode: table, STDLOG:       0 UPD                        3
    checked_mode: table, STDLOG:       1 UPD                        3
    checked_mode: table, STDLOG:       0 UPD                        4
    checked_mode: table, STDLOG:       1 UPD                        4
    checked_mode: table, STDLOG:       0 UPD                        5
    checked_mode: table, STDLOG:       1 UPD                        5

    checked_mode: table, STDLOG: Records affected: 10
    checked_mode: table, STDERR: Statement failed, SQLSTATE = 21000
    checked_mode: table, STDERR: Multiple source records cannot match the same target during MERGE
    checked_mode: table, STDERR: After line
    checked_mode: view, STDLOG: Records affected: 2

    checked_mode: view, STDLOG:      ID       X
    checked_mode: view, STDLOG: ======= =======
    checked_mode: view, STDLOG:      -5       5
    checked_mode: view, STDLOG:      -4       4
    checked_mode: view, STDLOG:      -3       3
    checked_mode: view, STDLOG:      -2       2
    checked_mode: view, STDLOG:      -1       1
    checked_mode: view, STDLOG:       0       0
    checked_mode: view, STDLOG:       1       1

    checked_mode: view, STDLOG: Records affected: 7

    checked_mode: view, STDLOG:  OLD_ID OP              SNAP_NO_RANK
    checked_mode: view, STDLOG: ======= ====== =====================
    checked_mode: view, STDLOG:       0 UPD                        1
    checked_mode: view, STDLOG:       1 UPD                        1
    checked_mode: view, STDLOG:       0 UPD                        2
    checked_mode: view, STDLOG:       1 UPD                        2
    checked_mode: view, STDLOG:       0 UPD                        3
    checked_mode: view, STDLOG:       1 UPD                        3
    checked_mode: view, STDLOG:       0 UPD                        4
    checked_mode: view, STDLOG:       1 UPD                        4
    checked_mode: view, STDLOG:       0 UPD                        5
    checked_mode: view, STDLOG:       1 UPD                        5

    checked_mode: view, STDLOG: Records affected: 10
    checked_mode: view, STDERR: Statement failed, SQLSTATE = 21000
    checked_mode: view, STDERR: Multiple source records cannot match the same target during MERGE
    checked_mode: view, STDERR: After line
"""

def wait_for_attach_showup_in_monitoring(con_monitoring, sql_text_tag):
    chk_sql = f"select 1 from mon$statements s where s.mon$attachment_id != current_connection and s.mon$sql_text containing '{sql_text_tag}'"
    attach_with_sql_tag = None
    t1=py_dt.datetime.now()
    cur_monitoring = con_monitoring.cursor()
    while True:
        cur_monitoring.execute(chk_sql)
        for r in cur_monitoring:
            attach_with_sql_tag = r[0]
        if not attach_with_sql_tag:
            t2=py_dt.datetime.now()
            d1=t2-t1
            if d1.seconds*1000 + d1.microseconds//1000 >= MAX_WAIT_FOR_WORKER_START_MS:
                break
            else:
                con_monitoring.commit()
                time.sleep(0.2)
        else:
            break
            
    assert attach_with_sql_tag, f"Could not find attach statement containing '{sql_text_tag}' for {MAX_WAIT_FOR_WORKER_START_MS} ms. ABEND."
    return

@pytest.mark.version('>=4.0')
def test_1(act: Action, fn_worker_sql: Path, fn_worker_log: Path, fn_worker_err: Path, capsys):
    sql_init = (act.files_dir / 'read-consist-sttm-restart-DDL.sql').read_text()

    for checked_mode in('table', 'view'):
        target_obj = 'test' if checked_mode == 'table' else 'v_test'

        SQL_TO_BE_RESTARTED = f"""
            merge /* {SQL_TAG_THAT_WE_WAITING_FOR} */ into {target_obj} t
                using (
                    select s.id, s.x from {target_obj} as s
                    where s.id <= 1
                    order by s.id DESC
                ) s
                on abs(t.id) = abs(s.id)
            when matched then
                update set t.x = t.x * s.x
            ;
        """

        sql_addi = f'''
            set term ^;
            execute block as
            begin
                rdb$set_context('USER_SESSION', 'WHO', 'INIT_DATA');
            end
            ^
            set term ;^

             -- INITIAL DATA: add rows with ID = 0...6
             -- #############
            insert into {target_obj}(id, x)
            select row_number()over()-1, row_number()over()-1
            from rdb$types rows 6;

            commit;
        ''' % locals()

        act.isql(switches=['-q'], input = ''.join( (sql_init, sql_addi) ) )
        # ::: NOTE ::: We have to immediately quit if any error raised in prepare phase.
        # See also letter from dimitr, 01-feb-2022 14:46
        assert act.stderr == ''
        act.reset()

        with act.db.connect() as con_lock_1, act.db.connect() as con_lock_2, act.db.connect() as con_monitoring:
            cur_lock_1 = con_lock_1.cursor()
            cur_lock_2 = con_lock_2.cursor()

            for i,c in enumerate((con_lock_1,con_lock_2)):
                sttm = f"execute block as begin rdb$set_context('USER_SESSION', 'WHO', 'LOCKER #{i+1}'); end"
                c.execute_immediate(sttm)


            #########################
            ###  L O C K E R - 1  ###
            #########################

            con_lock_1.execute_immediate( f'update {target_obj} set id=id where id = 0' )

            worker_sql = f'''
                set list on;
                set autoddl off;
                set term ^;
                execute block as
                begin
                    rdb$set_context('USER_SESSION','WHO', 'WORKER');
                end
                ^
                set term ;^
                commit;
                SET KEEP_TRAN_PARAMS ON;
                set transaction read committed read consistency;
                set list off;
                set wng off;

                set count on;

                -- this must hangs because of locker-1:
                {SQL_TO_BE_RESTARTED};

                -- check results:
                -- ###############

                select id,x from {target_obj} order by id;

                select v.old_id, v.op, v.snap_no_rank
                from v_worker_log v
                where v.op = 'upd';


                --set width who 10;
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

                wait_for_attach_showup_in_monitoring(con_monitoring, SQL_TAG_THAT_WE_WAITING_FOR)

                sttm = f'update {target_obj} set id = ? where abs( id ) = ?'

                #########################
                ###  L O C K E R - 2  ###
                #########################
                cur_lock_2.execute( sttm, ( -5, 5, ) )
                con_lock_2.commit()
                cur_lock_2.execute( sttm, ( -5, 5, ) )

                #########################
                ###  L O C K E R - 1  ###
                #########################
                con_lock_1.commit()
                cur_lock_1.execute( sttm, ( -4, 4, ) )
                con_lock_1.commit()
                cur_lock_1.execute( sttm, ( -4, 4, ) )

                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_2.commit()
                cur_lock_2.execute( sttm, ( -3, 3, ) )
                con_lock_2.commit()
                cur_lock_2.execute( sttm, ( -3, 3, ) )

                #########################
                ###  L O C K E R - 1  ###
                #########################
                con_lock_1.commit()
                cur_lock_1.execute( sttm, ( -2, 2, ) )
                con_lock_1.commit()
                cur_lock_1.execute( sttm, ( -2, 2, ) )

                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_2.commit()
                cur_lock_2.execute( f'insert into {target_obj}(id,x) values(?, ?)', ( -1, 1, ) )
                con_lock_2.commit()
                cur_lock_2.execute( f'update {target_obj} set id = id where id = ?', ( -1, ) )

                #########################
                ###  L O C K E R - 1  ###
                #########################
                con_lock_1.commit()

                #########################
                ###  L O C K E R - 2  ###
                #########################
                con_lock_2.commit() # At this point merge can complete its job but it must FAIL because of multiple matches for abs(t.id) = abs(s.id), i.e. when ID = -1 and 1

                # Here we wait for ISQL complete its mission:
                p_worker.wait()


        for g in (fn_worker_log, fn_worker_err):
            log_type = 'STDLOG' if g == fn_worker_log else 'STDERR'
            with g.open() as f:
                for line in f:
                    if line.split():
                        print(f'checked_mode: {checked_mode}, {log_type}: {line}')

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

