#coding:utf-8

"""
ID:          issue-5015
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/5015
TITLE:       Implement ability to validate tables and indices online (without exclusive access to database)
DESCRIPTION:
    Test verifies ability to run online validation during 'static' state of database with one connection
    which has done several incomplete DML and stands in endless pause (because of `WAIT` transaction and attempt
    to change via ES/EDS some record that has been already locked).
JIRA:        CORE-4707
FBTEST:      bugs.core_4707
NOTES:
    [19.09.2026] pzotov
    Test has been significantly reworked after receiving notes from ZCODE.AI about waiting via `time.sleep(2)`.
    This pause starts just after async launch os ISQL in order to let this process to load in memory and complete code
    that eventually falls into infinite waiting. Online validation should start only after this pause completed.
    This way is unreliable: under heavy concurrent workload ISQL may not complete its work (or even does not load in memory)
    and online validation will not check what it should because some table(s) either not exist or one of them not yet locked.
    
    To avoid this, we have to run auxiliary connect (`con_monitoring`) which has to perform loop and check presence of
    ISQL process in mon$attachments and, moreover, check that value of generator `g` is greater than 0 (this will prove that
    ISQL has started `WAIT` transaction and stands now in endless waiting for record that is locked).

    After this connect will detect such record and verify value of generator, we can break from monitoring loop and start
    online validation. After validation finish, we have to terminate async ISQL process and check validation output.
    If this connect could not be found during some limit (see `MAX_WAIT_FOR_WORKER_START_MS`) then we
    have to terminate async ISQL, break from loop and run assertion with showing ISQL log.

    ### CRITICAL ISSUE-1 ###
    Asynchronously launched ISQL (see `p_hang_sql`) keeps opened .sql and .log files created using fixture `temp_file()`.
    It was found that after call its p_hang_sql.terminate() these logs may live BEYOND this process is gone. Main reason:
    https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess
    ("TerminateProcess is asynchronous; it initiates termination and returns immediately.")
    This caused PermissionError (32) at teardown stage: one of both of them could not be deleted because they still were
    opened by OS (though for a short time).
    This was explained by zcode.ai (together with suggested fix - see call of `terminate_sync()` function from QA-plugin).

    ### CRITICAL ISSUE-2 ###
    We have to issue 'SET STATEMENT TIMEOUT 0' in order to be sure that async ISQL stands in long-term waiting and its hanging 
    statement will not be cancelled because of relatively small value of `StatementTimeout` parameter from firebird.conf.
    Statement and connection timeouts were introduced in
    4.0.0-2c49e6fc / 22.02.2017 12:30:57 ("New feature CORE-5488 : Timeouts for running SQL statements and idle connections")

    Checked on 6.0.0.2176; 5.0.5.1886; 4.0.8.3320; 3.0.15.33885.
"""
import pytest
import subprocess
import time
import datetime as py_dt
from pathlib import Path
from firebird.qa import *

MAX_WAIT_FOR_WORKER_START_MS = 20000

init_script = """
    recreate sequence g;
    commit;
    -- this table will NOT be validated because of incompleted `UPDATE` against it:
    recreate table test1(id int, s varchar(1000));

    -- this table MUST be validated:
    recreate table test2(id int primary key using index test2_pk, s varchar(1000), t computed by (s) );

    -- this table will NOT be validated because of incompleted `INSERT` against it:
    recreate table test3(id int);
    commit;

    insert into test1(id, s) select row_number()over(), rpad('', 1000, uuid_to_char(gen_uuid())) from rdb$types rows 100;
    insert into test2(id, s) select id, s from test1;
    commit;

    create index test2_s on test2(s);
    create index test2_c on test2 computed by(s);
    create index test2_t on test2 computed by(t);
    commit;
"""

# Name of alias that will be written into temporary replacement of databases.conf:
CONNECT_TO_ALIAS = 'tmp_core_4707_alias'

db = db_factory(init=init_script)

substitutions=[ ('\\d{2}:\\d{2}:\\d{2}.\\d{2}', ''), ('Relation \\d{3,4}', 'Relation'), ('[ \t]+', ' ') ]
act = python_act('db', substitutions = substitutions)

tmp_hang_sql = temp_file('tmp_hanging_4707.sql')
tmp_hang_log = temp_file('tmp_hanging_4707.log')

@pytest.mark.ai
@pytest.mark.es_eds
@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_hang_sql: Path, tmp_hang_log: Path, capsys):

    get_sttm_timeout = "select * from rdb$config where lower(rdb$config_name) = lower('StatementTimeout')"
    set_sttm_timeout = "set statement timeout 0"
    if act.is_version('<4'):
        get_sttm_timeout = ''
        set_sttm_timeout = ''

    # Following script will hang for endless waiting ==> we can start online validation
    # when mon$attachment will contain record of appriate async ISQL:
    tmp_hang_sql.write_text(
        f"""
            set echo on;
            set list on;
            set count on;
            {get_sttm_timeout};
            commit;
            set transaction wait;
            delete from test1;
            insert into test3(id) values(1);
            select 'Starting EB with infinite pause.' as isql_msg from rdb$database;
            {set_sttm_timeout};
            set term ^;
            execute block as
            begin
                execute statement ('update test1 set id = -id where id = ?') ( gen_id(g,1) )
                on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
                as user '{act.db.user}' password '{act.db.password}'
                ;
                -- Discussed with Vlad, letters 29.03.2025 ... 09.04.2025
                -- subj: "WI-6.0.0.707-4bd4f5f0, Classic. CORE-4707 (online validation): ..."
                -- COMMENTED 30.03.2025: we must know if some error occurred during infinite wait! --> when any do begin end
                -- ::: NB ::: ON LINUX THIS TEST CAN STILL FAIL, THE REASON REMAINS UNKNOWN :::
            end ^
            set term ;^
            select 'EB with pause finished.' as msg_2 from rdb$database;
        """
    )

    worker_attach_id = 0
    in_locked_state = False
    p_hang_sql = None
    validation_output = ''
    with open(tmp_hang_log, mode='w') as f_hang_log:
        try:
            # Create connection for watching mon$attachments: we are waiting appearance
            # of ISQL process which has to hang on lock conflict in EDS statement.
            # Each iteration opens and completes its own transaction, see core_5685_test.py:
            #
            with act.db.connect() as con_monitoring:
                cur_monitoring = con_monitoring.cursor()

                sql_watched = """
                    select /* trace_me */ mon$attachment_id from mon$attachments
                    where
                        mon$attachment_id != current_connection
                        and trim(lower(mon$remote_process)) similar to '%[\\/]isql(.exe)?'
                """

                iter = 0
                t1 = py_dt.datetime.now()
                while True:
                    if iter == 0:
                        #########################
                        ###   'w o r k e r'   ###
                        #########################
                        # Asynchronous launch ISQL which will be blocked infinitely in pause due to row-level lock
                        p_hang_sql = subprocess.Popen([act.vars['isql'], '-i', str(tmp_hang_sql),
                                                       '-user', act.db.user,
                                                       '-password', act.db.password, act.db.dsn],
                                                      stdout=f_hang_log, stderr=subprocess.STDOUT)

                    con_monitoring.begin()
                    try:
                        cur_monitoring.execute(sql_watched)
                        worker_attach_id = cur_monitoring.fetchone()
                        if worker_attach_id:
                            try:
                                cur_monitoring.execute('select gen_id(g,0) from rdb$database')
                                in_locked_state = cur_monitoring.fetchone()[0] > 0
                            except DatabaseError:
                                in_locked_state = False
                    finally:
                        con_monitoring.rollback()

                    if worker_attach_id and in_locked_state:

                        ###############################################
                        ###    o n l i n e    v a l i d a t i o n   ###
                        ###############################################
                        # Validate database which has connection that infinitely waits for on some resource:
                        act.svcmgr(switches=['action_validate', 'dbname', str(act.db.db_path), 'val_lock_timeout', '1'])
                        validation_output = act.stdout
                        act.reset() 

                        break

                    if p_hang_sql.poll() is not None:
                        # ISQL has completed: nothing to wait for more (this is possible
                        # only if its script failed to hang; assert below will show its log).
                        break

                    t2 = py_dt.datetime.now()
                    d1 = t2 - t1
                    if d1.seconds * 1000 + d1.microseconds // 1000 >= MAX_WAIT_FOR_WORKER_START_MS:
                        break
                    else:
                        time.sleep(0.2)

                    iter += 1
                # < while True

            #< with act.db.connect() as con_monitoring

        except Exception as e:
            print(f'{e.__class__=}')
            print(e.__str__())

        finally:
            # suggested by ZCODE.AI, added to QA plugin 19.09.2026. Source code see in QA-plugin:
            terminate_sync(p_hang_sql)

    # < with open(tmp_hang_log, mode='w')

    if not (worker_attach_id and in_locked_state):
        isql_log = '\n'.join( [ x for x in tmp_hang_log.read_text().splitlines() if x.strip() ] )
        print(f"Could not detect ISQL process with established connection and locked resource for {MAX_WAIT_FOR_WORKER_START_MS} ms. Check its log:\n" + isql_log)

    print(validation_output)

    expected_stdout_5x = """
        Validation started
        Relation (TEST1)
        Acquire relation lock failed
        Relation (TEST1) : 1 ERRORS found
        Relation (TEST2)
        process pointer page    0 of    1
        Index 1 (TEST2_PK)
        Index 2 (TEST2_S)
        Index 3 (TEST2_C)
        Index 4 (TEST2_T)
        Relation (TEST2) is ok
        Relation (TEST3)
        Acquire relation lock failed
        Relation (TEST3) : 1 ERRORS found
        Validation finished
    """

    expected_stdout_6x = """
        Validation started
        Relation ("PUBLIC"."TEST1")
        Acquire relation lock failed
        Relation ("PUBLIC"."TEST1") : 1 ERRORS found
        Relation ("PUBLIC"."TEST2")
        process pointer page    0 of    1
        Index 1 ("PUBLIC"."TEST2_PK")
        Index 2 ("PUBLIC"."TEST2_S")
        Index 3 ("PUBLIC"."TEST2_C")
        Index 4 ("PUBLIC"."TEST2_T")
        Relation ("PUBLIC"."TEST2") is ok
        Relation ("PUBLIC"."TEST3")
        Acquire relation lock failed
        Relation ("PUBLIC"."TEST3") : 1 ERRORS found
        Validation finished
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
