#coding:utf-8

"""
ID:          issue-7304
ISSUE:       7304
TITLE:       Events in system attachments (like garbage collector) are not traced
DESCRIPTION:
    Test changes sweep interval to some low value (see SWEEP_GAP) and runs TX_COUNT transactions which
    lead difference between OST and OIT to exceed given sweep interval. These transactions are performed
    by ISQL which is launched as child process. SQL script uses table with record that is locked at the 
    beginning of script and execute block with loop of TX_COUNT statements which insert new records.
    After this loop finish, we make ISQL to hang by forcing it to update first record (see LOCKED_ROW).
    Then we change DB state to full shutdown and wait until ISQL will be terminated.
    At this point database has sweep gap that is enough to run auto sweep at first connection to DB.
    Finally, we bring DB online and start trace with log_sweep =  true and log_transactions = true.
    Doing connection and wait about 2..3 seconds cause auto sweep to be started and completed.
    This must be reflected in the trace.

    If ServerMode = 'Super' and ParallelWorkers >= 2 and MaxParallelWorkers >= ParallelWorkers
    then trace log will contain folloing five lines related to worker(s) activity:
       <TIMESTAMP> (...) START_TRANSACTION
       <DBFILE> (ATT_..., <Worker>, NONE, <internal>) --------------------- [ 1 ]
       (TRA_..., READ_COMMITTED | REC_VERSION | WAIT | READ_ONLY)
       <TIMESTAMP> (...) COMMIT_TRANSACTION
       <DBFILE> (ATT_..., <Worker>, NONE, <internal>) --------------------- [ 2 ]

    This is the only difference that can be observed for snapshots before and after fix
    (i.e. BEFORE fix trace had no such lines but all other data about sweep *did* present).
    Test checks that trace log contains TWO lines with '<worker>', see above [ 1 ] and [ 2 ].

JIRA:        CORE-2668
FBTEST:      bugs.core_2668
NOTES:
    [07.11.2024] pzotov
    Confirmed absense of lines marked as '<worker' in the trace log for snapshot 5.0.0.731 (15.09.2022).
    Checked on 5.0.0.733 (16.09.2022); 5.0.2.1553, 6.0.0.515
"""

import time
import subprocess
from datetime import datetime as dt
import re
from pathlib import Path
from difflib import unified_diff
from firebird.driver import DatabaseError, tpb, Isolation, TraLockResolution, DbWriteMode, ShutdownMode, ShutdownMethod

import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db', substitutions = [('\\(ATT_\\d+', '(ATT_N')])

################
### SETTINGS ###
################
SWEEP_GAP = 100
TX_COUNT = 150
LOCKED_ROW = -1
MAX_WAIT_FOR_ISQL_PID_APPEARS_MS = 5000
WATCH_FOR_PTN = re.compile( r'\(ATT_\d+,\s+<Worker>,\s+NONE,\s+<internal>\)', re.IGNORECASE)
################

tmp_sql = temp_file('tmp_2668.sql')
tmp_log = temp_file('tmp_2668.log')

@pytest.mark.es_eds
@pytest.mark.version('>=5.0.0')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path, capsys):

    if act.vars['server-arch'] != 'SuperServer':
        pytest.skip("Applies only to SuperServer")

    with act.db.connect() as con:
        cur = con.cursor()
        sql = """
            select
                 cast(max(iif(g.rdb$config_name = 'ParallelWorkers', g.rdb$config_value, null)) as int) as cfg_par_workers
                ,cast(max(iif(g.rdb$config_name = 'MaxParallelWorkers', g.rdb$config_value, null)) as int) as cfg_max_par_workers
            from rdb$database
            left join rdb$config g on g.rdb$config_name in ('ParallelWorkers', 'MaxParallelWorkers')
        """
        cur.execute(sql)
        cfg_par_workers, cfg_max_par_workers = cur.fetchone()

        assert cfg_par_workers >=2 and cfg_max_par_workers >= cfg_par_workers, "Server must be configured for parallel work. Check values of ParallelWorkers and MaxParallelWorkers"

    test_script = f"""
        set echo on;
        set bail on;
        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';

        recreate table test(id int primary key);
        insert into test(id) values({LOCKED_ROW});
        commit;

        set transaction read committed WAIT;

        update test set id = id where id = {LOCKED_ROW};
        set term ^;
        execute block as
            declare n int = {TX_COUNT};
            declare v_role varchar(31);
        begin
            while (n > 0) do
                in autonomous transaction do
                insert into test(id) values(:n)
                returning :n-1 into n;

            v_role = left(replace( uuid_to_char(gen_uuid()), '-', ''), 31);

            begin
                execute statement ('update test /* ' || ascii_char(65) || ' */ set id = id where id = ?') ({LOCKED_ROW})
                on external
                    'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
                    as user '{act.db.user}' password '{act.db.password}' role v_role
                with autonomous transaction;
            when any do
                begin
                end
            end

        end
        ^
        set term ;^
        set heading off;
        select '-- shutdown me now --' from rdb$database;
    """
    
    tmp_sql.write_text(test_script)
    with act.connect_server() as srv:
        ##############################
        ### reduce SWEEEP interval ###
        ##############################
        srv.database.set_sweep_interval(database = act.db.db_path, interval = SWEEP_GAP)
        srv.database.set_write_mode(database=act.db.db_path, mode=DbWriteMode.ASYNC)

        with open(tmp_log,'w') as f_log:
            p_work_sql = subprocess.Popen([act.vars['isql'], '-q', '-i', str(tmp_sql)], stdout = f_log, stderr = subprocess.STDOUT)

            chk_mon_sql = """
                select 1
                from mon$attachments a
                join mon$statements s
                using (mon$attachment_id)
                where
                    a.mon$attachment_id <> current_connection
                    and cast(s.mon$sql_text as varchar(8192)) containing '/* A */'
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
                    cur_watcher.execute(ps)
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
                ##############################################
                ###   f u l l     s h u t d o w n    D B   ###
                ##############################################
                srv.database.shutdown(database=act.db.db_path, mode=ShutdownMode.FULL,
                                      method=ShutdownMethod.FORCED, timeout=0)
            finally:
                p_work_sql.terminate()
        # < with open(tmp_log,'w') as f_log

        srv.database.bring_online(database=act.db.db_path)

    trace_options = \
        [
             'time_threshold = 0'
            ,'log_initfini = false'
            ,'log_connections = true'
            ,'log_transactions = true'
            ,'log_errors = true'
            ,'log_sweep = true'
        ]

    with act.trace(db_events = trace_options, encoding='utf8', encoding_errors='utf8'):
        with act.db.connect() as con_for_sweep_start:
            time.sleep(2)


    for line in act.trace_log:
        if WATCH_FOR_PTN.search(line):
            print(WATCH_FOR_PTN.search(line).group())

    act.expected_stdout = """
        (ATT_N, <Worker>, NONE, <internal>)
        (ATT_N, <Worker>, NONE, <internal>)
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
