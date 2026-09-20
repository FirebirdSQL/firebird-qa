#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/4710
TITLE:       SELECT WITH LOCK may enter an infinite loop for a single record
DESCRIPTION:
JIRA:        CORE-4388
FBTEST:      bugs.core_4388
NOTES:
    [20.09.2026] pzotov
    The ticket was created in 2014 when 3.0 Alpha was in development.
    Current version of firebird-driver does not work with such old FB, so this bug could not be reproduced.

    Test has been significantly reworked after receiving notes from ZCODE.AI about waiting via `time.sleep(2)`.
    This pause starts just after async launch os ISQL in order to let this process to load in memory and complete code
    that eventually falls into infinite or long-term waiting. 
    This way is unreliable: under heavy concurrent workload ISQL may not complete its work (or even does not load in memory)
    and test will not check what it should because some table(s) either not exist or one of them not yet locked.
    
    To avoid this, we have to run auxiliary connect (`con_monitoring`) which has to perform loop and check presence of
    ISQL process in mon$attachments and, moreover, check that value of generator `g` is greater than 0 (this will prove that
    ISQL has started `WAIT` transaction and stands now in endless waiting for record that is locked).

    After this connect will detect such record and verify value of generator, we can break from monitoring loop and start
    online validation. After validation finish, we have to terminate async ISQL process and check validation output.
    If this connect could not be found during some limit (see `MAX_WAIT_FOR_HANGED_ASYNC_ISQL_MS`) then we
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

init_script = """
    create sequence g;
    create table test(id int primary key, x int);
    commit;
    insert into test values(1, 100);
    commit;
"""

# Name of alias that will be written into temporary replacement of databases.conf:
CONNECT_TO_ALIAS = 'tmp_core_4388_alias'

MAX_WAIT_FOR_HANGED_ASYNC_ISQL_MS = 20000

db = db_factory(sql_dialect=3, init=init_script)

substitutions = [ ('(-)?concurrent\\s+transaction\\s+number(\\s+is)?\\s+\\d+','concurrent transaction')
                  ,('After\\s+line\\s+\\d+.*', '')
                  ,('[ \t]+', ' ')
                ]
act = python_act('db', substitutions = substitutions)

tmp_hang_sql = temp_file('tmp_4388.sql')
tmp_hang_log = temp_file('tmp_4388.log')

@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_hang_sql: Path, tmp_hang_log: Path, capsys):

    set_sttm_timeout = "set statement timeout 0"
    if act.is_version('<4'):
        set_sttm_timeout = ''

    hanged_script = f"""
        --set echo on;
        set list on;
        select gen_id(g,1) from rdb$database;
        {set_sttm_timeout};
        commit;
        set transaction lock timeout 20;
        select /* trace_me */ x from test where id = 1 with lock;
    """

    tmp_hang_sql.write_text(hanged_script)

    hanged_attach_id = 0
    in_locked_state = False
    p_hang_sql = None
    with open(tmp_hang_log, mode='w') as f_hang_log:
        with act.db.connect() as con_aux:
            try:
                # con_aux: delete record but not commit
                con_aux.execute_immediate("delete /* trace_me */ from test where id = 1")

                # Create connection for watching mon$attachments: we are waiting appearance
                # of ISQL process which has to hang on lock conflict in EDS statement.
                # Each iteration opens and completes its own transaction, see core_5685_test.py:
                #
                with act.db.connect() as con_monitoring:
                    
                    cur_monitoring = con_monitoring.cursor()

                    sql_watched = f"""
                        select /* trace_me */ mon$attachment_id from mon$attachments
                        where
                            mon$attachment_id != current_connection
                            and trim(lower(mon$remote_process)) = trim(lower('{act.vars["isql"]}'))
                    """

                    iter = 0
                    t1 = py_dt.datetime.now()
                    while True:
                        if iter == 0:
                            ##################################
                            ###   'A S Y N C    I S Q L'   ###
                            ##################################
                            # Asynchronous launch ISQL which will be in long-term blocked state due to row-level lock
                            p_hang_sql = subprocess.Popen( [act.vars['isql'], '-i', str(tmp_hang_sql),
                                                           '-user', act.db.user,
                                                           '-password', act.db.password, act.db.dsn],
                                                           stdout=f_hang_log,
                                                           stderr=subprocess.STDOUT,
                                                          )

                        con_monitoring.begin()
                        try:
                            cur_monitoring.execute(sql_watched)
                            hanged_attach_id = cur_monitoring.fetchone()
                            if hanged_attach_id:
                                try:
                                    cur_monitoring.execute('select /* trace_me */ gen_id(g,0) from rdb$database')
                                    in_locked_state = cur_monitoring.fetchone()[0] > 0
                                except DatabaseError:
                                    in_locked_state = False
                        finally:
                            con_monitoring.rollback()

                        if p_hang_sql.poll() is not None:
                            # ISQL has completed: nothing to wait anymore (this is possible
                            # only if its script failed to hang; assert below will show its log).
                            print('Child async ISQL either did not start or completed too fast.')
                            break

                        if hanged_attach_id and in_locked_state:
                            break

                        t2 = py_dt.datetime.now()
                        d1 = t2 - t1
                        if d1.seconds * 1000 + d1.microseconds // 1000 >= MAX_WAIT_FOR_HANGED_ASYNC_ISQL_MS:
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
                if hanged_attach_id and in_locked_state:
                    con_aux.commit()
                    if p_hang_sql:
                        # we must allow async ISQL to flush its output!
                        # Otherwise only 'GEN_ID 1' will be in tmp_hang_log.
                        p_hang_sql.wait()

                # suggested by ZCODE.AI, added to QA plugin 19.09.2026. Source code see in QA-plugin:
                terminate_sync(p_hang_sql)
        # < with act.db.connect() as con_aux
    # < with open(tmp_hang_log, mode='w')

    print(tmp_hang_log.read_text())
    act.expected_stdout = """
        GEN_ID 1
        Statement failed, SQLSTATE = 40001
        deadlock
        -update conflicts with concurrent update
        -concurrent transaction number is 13
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
