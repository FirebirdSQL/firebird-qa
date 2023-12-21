#coding:utf-8

"""
ID:          issue-6691
ISSUE:       6691
TITLE:       Regression: Cancel Query function no longer works
DESCRIPTION:
  We create .sql script with 'heavy query' that for sure will run more than several seconds.
  Then we launch asynchronously ISQL to perform this query and wait until its PID and running
  query will appear in the mon$ tables (we are looking for query that containing text 'HEAVY_TAG').

  After this we send signal CTRL_C_EVENT for emulating interruption that is done by pressing Ctrl-C.
  Then we wait for process finish (call wait() method) - this is necessary if ISQL will continue
  without interruprion (i.e. if something will be broken again).

  When method wait() will return control back, we can obtain info about whether child process was
  terminated or no (using method poll()). If yes (expected) then it must return 1.

  Finally, we check ISQL logs for STDOUT and STDERR. They must be as follows:
  * STDOUT -- must be empty
  * STDERR -- must contain (at least) two phrases:
    1. Statement failed, SQLSTATE = HY008
    2. operation was cancelled

  ::: NB :::
  Windows only: subprocess.Popen() must have argument: creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
  Otherwise we can not send signal Ctrl_C_EVENT to the child process.
  Linux: parameter 'creationflags' must be 0, signal.SIGINT is used instead of Ctrl_C_EVENT.

  See: https://docs.python.org/2.7/library/subprocess.html

  Confirmed bug on 4.0.0.2307: query could NOT be interrupted and we had to wait until it completed.
  Checked on 4.0.0.2324 (SS/CS): works OK, query can be interrupted via sending Ctrl-C signal.

JIRA:        CORE-6458
FBTEST:      bugs.core_6458
"""

import re
import signal
import subprocess
from datetime import datetime as dt
import time
from pathlib import Path
from firebird.driver import DatabaseError, tpb, Isolation, TraLockResolution, DatabaseError

import pytest
from firebird.qa import *

MAX_WAIT_FOR_ISQL_PID_APPEARS_MS = 10000
HEAVY_TAG = '/* HEAVY_TAG */'

db = db_factory()

act = python_act('db')

expected_stdout = """
    Was ISQL process terminated ? =>  1
    statement failed, sqlstate = hy008
    operation was cancelled
"""

heavy_script = temp_file('heavy_script.sql')
heavy_stdout = temp_file('heavy_script.out')
heavy_stderr = temp_file('heavy_script.err')

@pytest.mark.version('>=4.0')
def test_1(act: Action, heavy_script: Path, heavy_stdout: Path, heavy_stderr: Path,
           capsys):
    heavy_script.write_text(f"set list on; select {HEAVY_TAG} count(*) as LONG_QUERY_RESULT from (select 1 i from rdb$types a,rdb$types b,rdb$types c,rdb$types d,rdb$types e);")
    with open(heavy_stdout, mode='w') as heavy_out, open(heavy_stderr, mode='w') as heavy_err:
        # NB: subprocess.CREATE_NEW_PROCESS_GROUP is MANDATORY FOR SENDING CTRL_C SIGNAL on Windows
        flags = 0 if act.platform == 'Linux' else subprocess.CREATE_NEW_PROCESS_GROUP
        p_heavy_sql = subprocess.Popen( [ act.vars['isql'],
                                          '-i', str(heavy_script),
                                          '-user', act.db.user,
                                          '-password', act.db.password,
                                          act.db.dsn
                                        ],
                                        stdout=heavy_out,
                                        stderr=heavy_err,
                                        creationflags=flags
                                      )
        
        chk_mon_sql = """
            select 1
            from mon$attachments a
            join mon$statements s
            using (mon$attachment_id)
            where
                a.mon$attachment_id <> current_connection
                and a.mon$remote_pid = ?
                and s.mon$sql_text containing ?
        """

        found_in_mon_tables = False
        with act.db.connect() as con_watcher:

            custom_tpb = tpb(isolation = Isolation.SNAPSHOT, lock_timeout = -1)
            tx_watcher = con_watcher.transaction_manager(custom_tpb)
            cur_watcher = tx_watcher.cursor()

            ps = cur_watcher.prepare(chk_mon_sql)

            i = 0
            da = dt.now()
            while True:
                cur_watcher.execute(ps, (p_heavy_sql.pid, HEAVY_TAG,) )
                mon_result = -1
                for r in cur_watcher:
                    mon_result = r[0]

                tx_watcher.commit()
                db = dt.now()
                diff_ms = (db-da).seconds*1000 + (db-da).microseconds//1000
                if mon_result == 1:
                    found_in_mon_tables = True
                    break
                elif diff_ms > MAX_WAIT_FOR_ISQL_PID_APPEARS_MS:
                    break

                time.sleep(0.1)

            ps.free()

        assert found_in_mon_tables, f'Could not find attachment in mon$ tables for {MAX_WAIT_FOR_ISQL_PID_APPEARS_MS} ms.'
        
        
        try:
            p_heavy_sql.send_signal(signal.SIGINT if act.platform == 'Linux' else signal.CTRL_C_EVENT)
            p_heavy_sql.wait()
            print('Was ISQL process terminated ? => ', p_heavy_sql.poll())
        except Exception as e:
            print(e)
    for line in heavy_stdout.read_text().splitlines():
        if line.split():
            print('UNEXPECTED STDOUT: ', line)
    allowed_patterns = [re.compile('.*SQLSTATE\\s+=\\s+HY008', re.IGNORECASE),
                        re.compile('operation\\s+(was\\s+)?cancelled', re.IGNORECASE)]
    for line in heavy_stderr.read_text().splitlines():
        if line.split():
            if act.match_any(line, allowed_patterns):
                print(' '.join(line.split()).lower())
    # Check
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
