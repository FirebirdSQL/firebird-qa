#coding:utf-8

"""
ID:          issue-8085
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8085
TITLE:       Memory leak when executing a lot of different queries and StatementTimeout > 0
DESCRIPTION:
    Test launches ISQL in async mode and then checks in loop for <MEMORY_MEASURE_COUNT> seconds value of memory that
    is consumed by psutil.Process( <fb_pid> ), where <fb_pid> is value of server PID that can be found in for ISQL
    in mon$attachments.mon$server_pid.
    Then we collect values of memory_info().rss returned by instance of psutil.Process( <fb_pid> ) in the list,
    see 'memo_rss_list' variable.
    Collection of memory_info().rss value is made with interval <MEMORY_MEASURE_INTERVAL> second. DO NOT SET IT LESS THAN 0.2!
    Finally, we evaluate differences between adjacent values from memo_rss_list.
    Median of these differences must be LESS THAN <MAX_RSS_KB_DIFF_MEDIAN> (Kb).
    Before fix this median was about 650K, after fix it is 0.
NOTES:
    [17.04.2024] pzotov
    Bug detected when test for gh-2388 was implementated (there is loop with ~20E6 iterations which run ES).

    [21.09.2026] pzotov
    Test has been significantly reworked after receiving notes from ZCODE.AI about waiting via `time.sleep(<N>)`.
    This pause started just after async launch os ISQL in order to let this process to load in memory and complete code
    that eventually falls into infinite/long-term waiting or running. Further code in test should continue only after
    this pause completion.
    This way is unreliable: under heavy concurrent workload ISQL may not complete its work (or even does not load in memory)
    and test will not check what it should.
    
    To avoid this, we have to run auxiliary connect (`con_monitoring`) which has to perform loop and check presence of
    ISQL process in mon$attachments and, moreover, verify that value of generator `g` is greater than 0 (this will prove
    that ISQL stands now in endless waiting or running).

    After this connect will detect such record and verify value of generator, we can break from monitoring loop and start
    further code. Otherwise, if connect from async ISQL could not be found during `MAX_WAIT_FOR_ISQL_STARTS_MS` seconds
    then we break from loop and run assertion with showing ISQL log.

    ### CRITICAL ISSUE-1 ###
    Asynchronously launched ISQL (see `p_async_isql`) keeps opened .sql and .log files created using fixture `temp_file()`.
    It was found that after call its p_async_isql.terminate() these logs may live BEYOND this process is gone. Main reason:
    https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess
    ("TerminateProcess is asynchronous; it initiates termination and returns immediately.")
    This caused PermissionError (32) at teardown stage: one of both of them could not be deleted because they still were
    opened by OS (though for a short time).
    This was explained by zcode.ai (together with suggested fix - see call of `terminate_sync()` function from QA-plugin).

    ### CRITICAL ISSUE-2 ###
    We have to issue 'SET STATEMENT TIMEOUT <N>' where <N> is greater <MAX_WAIT_FOR_ISQL_STARTS_MS> // 1000.
    Otherwise ISQL may be cancelled because of relatively small value of `StatementTimeout` parameter in firebird.conf.
    Statement and connection timeouts were introduced in
    4.0.0-2c49e6fc / 22.02.2017 12:30:57 ("New feature CORE-5488 : Timeouts for running SQL statements and idle connections")

    Confirmed bug on 6.0.0.313-aaf5faf
    Confirmed fix: 6.0.0.321-cc6fe45; 5.0.1.1381-0f3cdde; 4.0.5.3086-9d13bd3
    Checked on SS/CS, 6.0.0.2176; 5.0.5.1886; 4.0.8.3320
"""

import psutil
import pytest
import subprocess
import datetime as py_dt
import time
from pathlib import Path

import firebird.driver
from firebird.qa import *

db = db_factory()
act = python_act('db')

tmp_async_running_sql = temp_file('tmp_8085.sql')
tmp_async_running_log = temp_file('tmp_8085.log')

MAX_WAIT_FOR_ISQL_STARTS_MS=20000
MEMORY_MEASURE_COUNT = 31
MEMORY_MEASURE_INTERVAL = 0.3 # do not set this value less than 0.2
MAX_RSS_KB_DIFF_MEDIAN = 0

@pytest.mark.perf_measure
@pytest.mark.ai
@pytest.mark.version('>=4.0.5')
def test_1(act: Action, tmp_async_running_sql: Path, tmp_async_running_log: Path, capsys):

    test_sql = f"""
        recreate sequence g;
        recreate table tmplog(srv_pid int);
        commit;

        insert into tmplog(srv_pid) 
        select mon$server_pid as p
        from mon$attachments
        where mon$attachment_id = current_connection
        ;
        commit;
        
        SET STATEMENT TIMEOUT {int(1 + MAX_WAIT_FOR_ISQL_STARTS_MS//1000 + (MEMORY_MEASURE_COUNT-1) * MEMORY_MEASURE_INTERVAL)};
        set term ^;
        execute block as
            declare res double precision;
            declare v int = 0;
        begin
            while (1=1) do
            begin
                execute statement 'select ' || rand() || ' from rdb$database' into res;
                if ( v = 0 ) then
                    v = gen_id(g,1);
            end
        end
        ^
    """
    tmp_async_running_sql.write_text(test_sql)

    memo_rss_list = []
    memo_rss_diff = []
    hanged_attach_id = 0
    in_running_state = False
    p_async_isql = None
    srv_pid = None

    with open(tmp_async_running_log, 'w') as f:
        try:
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
                        # Asynchronous launch ISQL which will be in long-term or endless running state
                        p_async_isql = subprocess.Popen( [act.vars['isql'], '-e', '-i', str(tmp_async_running_sql),
                                                          '-user', act.db.user,
                                                          '-password', act.db.password, act.db.dsn],
                                                          stdout = f,
                                                          stderr = subprocess.STDOUT
                                                        )
                    con_monitoring.begin()
                    try:
                        cur_monitoring.execute(sql_watched)
                        hanged_attach_id = cur_monitoring.fetchone()
                        if hanged_attach_id:
                            try:
                                cur_monitoring.execute('select /* trace_me */ gen_id(g,0) from rdb$database')
                                in_running_state = cur_monitoring.fetchone()[0] > 0
                            except DatabaseError:
                                in_running_state = False
                    finally:
                        con_monitoring.rollback()

                    if p_async_isql and p_async_isql.poll() is not None:
                        # ISQL has completed: nothing to wait anymore (this is possible
                        # only if its script failed to hang; assert below will show its log).
                        print('Child async ISQL either did not start or completed too fast.')
                        cur_monitoring.execute('select /* trace_me */ 12345 from rdb$database')
                        break

                    if hanged_attach_id and in_running_state:
                        # ISQL is now running and performs endless loop with ES
                        cur_monitoring.execute('select srv_pid from tmplog')
                        srv_pid = cur_monitoring.fetchone()[0]
                        break

                    t2 = py_dt.datetime.now()
                    d1 = t2 - t1
                    if d1.seconds * 1000 + d1.microseconds // 1000 >= MAX_WAIT_FOR_ISQL_STARTS_MS:
                        break
                    else:
                        time.sleep(0.2)

                    iter += 1
                # < while True
            # < with act.db.connect() as con_monitoring

        except Exception as e:
            print(f'{e.__class__=}')
            print(e.__str__())
            raise
        finally:
            #assert hanged_attach_id
            #assert in_running_state
            if hanged_attach_id and in_running_state:
                fb_srv = psutil.Process( srv_pid )
                for i in range(MEMORY_MEASURE_COUNT):
                    memo_rss_list.append(int(fb_srv.memory_info().rss / 1024))
                    if i >= 1:
                        memo_rss_diff.append(memo_rss_list[i] - memo_rss_list[i-1])
    
                    time.sleep(MEMORY_MEASURE_INTERVAL)

            # suggested by ZCODE.AI, added to QA plugin 19.09.2026. Source code see in QA-plugin:
            terminate_sync(p_async_isql)
    
    # < with open(tmp_async_running_log, 'w') as f

    if not memo_rss_diff:
        isql_log = '\n'.join( [ x for x in tmp_async_running_log.read_text().splitlines() if x.strip() ] )
        print('Could not find running async ISQL, check its log:\n' + isql_log)
    else:
        memo_rss_diff_median = median(memo_rss_diff)
        median_acceptable_msg = 'Memory differences median acceptable.'
        if memo_rss_diff_median <= MAX_RSS_KB_DIFF_MEDIAN:
            print(median_acceptable_msg)
        else:
            print(f'Memory LEAK detected. Median of differences: {memo_rss_diff_median} Kb - is UNACCEPTABLE. Check memo_rss_diff:')
            for p in memo_rss_diff:
                print('%6d' % p)

    expected_stdout = f"""
        {median_acceptable_msg}
    """

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
