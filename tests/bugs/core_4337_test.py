#coding:utf-8

"""
ID:          issue-1535
ISSUE:       1535
TITLE:       gfix -sweep makes "reconnect" when it is removed from mon$attachments by delete command (issued in another window)
DESCRIPTION:
    We create table with several very wide char fields and fill it with uuid data.

    Then we create indexes for these fields and finally - delete all rows.
    Such table will require valuable time to be swept, about 4..5 seconds
    (we set DB forced_writes = ON and small buffers number in the DB header).

    After this we launch trace and 'gfix -sweep' (asynchronousl, via subprocess.Popen()).
    Then we immediately open cursor and start LOOP with query to mon$attachments.
    Loop will work until  connection created by gfix  will be seen there (usually this must occurs instantly).

    When gfix connection is known, we execute 'DELETE FROM MON$ATTACHMENT' command which should kill its attachment.
    Process of GFIX should raise error 'connection shutdown' - and we check this by saving its output to log.

    Further, we have to REPEAT check of mon$attachments after this and connection by 'gfix' must NOT present there.

    Then we stop trace and check its log. It must contain line with text 'SWEEP_FAILED' and after this line
    we should NOT discover any lines with 'ATTACH_DATABASE' event - this is especially verified.

    Finally, we compare content of firebird.log: new lines in it should contain messages about
    interrupted sweep ('error during sweep' and 'connection shutdown').
JIRA:        CORE-4337
FBTEST:      bugs.core_4337
NOTES:
    [26.09.2017]
        adjusted expected_stdout section to current FB 3.0+ versions: firebird.log now does contain info
        about DB name which was swept (see CORE-5610, "Provide info about database (or alias) which was in use...")
    [19.11.2021] pcisar
        Small difference in reimplementation of sweep killer script
        On v4.0.0.2496 COMMIT after delete from mon#attachments fails with:
        STATEMENT FAILED, SQLSTATE = HY008, OPERATION WAS CANCELLED
        Without commit this test PASSES, i.e. sweep is terminated with all outputs as expected
    [14.09.2022] pzotov
        Re-implemented: avoid usage of ISQL with fragile timeout setting (gfix can complete FASTER than isql will see it!).
        Appearance of 'gfix' process is checked in loop by querying mon$attachments, see also: MAX_WAIT_FOR_SWEEP_START_MS.
        More precise pattern for line with message about failed sweep (see 'p_sweep_failed').
        Checked on Windows and Linux: 3.0.8.33535 (SS/CS), 4.0.1.2692 (SS/CS), 5.0.0.730
    [22.02.2023] pzotov
    During run on 5.0.0.958 SS, "Windows fatal exception: access violation" error occurs and its full text + stack was 'embedded'
    in the pytest output. This error happens on garbage collection of Python code, when Statement destructor (__del__) was executed.
    Although all resources, including prepared statement, are used here within 'with' context manager, it will be good to put every
    'ps' usage inside 'with' block related to appropriate cursor. Before this, second 'ps' usage was linked to 1st [closed] cursor,
    so this may be relate4d somehow to this AV.
"""

import datetime as py_dt
from datetime import timedelta
import time

import subprocess
from difflib import unified_diff
import re
from pathlib import Path

from firebird.qa import *
from firebird.driver import DbWriteMode
import pytest

substitutions = [
                  ('[ ]+', ' '),
                  ('TRACE_LOG:.* SWEEP_START', 'TRACE_LOG: SWEEP_START'),
                  ('TRACE_LOG:.* SWEEP_FAILED', 'TRACE_LOG: SWEEP_FAILED'),
                  ('TRACE_LOG:.* ERROR AT JPROVIDER::ATTACHDATABASE', 'TRACE_LOG: ERROR AT JPROVIDER::ATTACHDATABASE'),
                  ('.*KILLED BY DATABASE ADMINISTRATOR.*', ''),
                  ('TRACE_LOG:.*GFIX.EXE.*', 'TRACE_LOG: GFIX.EXE'),
                  ('OIT [0-9]+', 'OIT'), ('OAT [0-9]+', 'OAT'), ('OST [0-9]+', 'OST'),
                  ('NEXT [0-9]+', 'NEXT'),
                  ('FIREBIRD.LOG:.* ERROR DURING SWEEP OF .*TEST.FDB.*', 'FIREBIRD.LOG: + ERROR DURING SWEEP OF TEST.FDB')
                ]

init_sql = """
    set list on;
    recreate table t(
         s01 varchar(4000)
        ,s02 varchar(4000)
        ,s03 varchar(4000)
        ,s04 varchar(4000)
    );
    commit;
    set term ^;
    execute block as
        declare n int = 20000;
        declare w int;
    begin
        select f.rdb$field_length
        from rdb$relation_fields rf
        join rdb$fields f on rf.rdb$field_source=f.rdb$field_name
        where rf.rdb$relation_name=upper('t') and rf.rdb$field_name=upper('s01')
        into w;

        while (n>0) do
            insert into t(s01, s02, s03, s04)
            values(
                       rpad('', :w, uuid_to_char(gen_uuid())) 
                      ,rpad('', :w, uuid_to_char(gen_uuid())) 
                      ,rpad('', :w, uuid_to_char(gen_uuid())) 
                      ,rpad('', :w, uuid_to_char(gen_uuid())) 
                  ) 
            returning :n-1 into n
        ;
    end^
    set term ;^
    commit;
    create index t_s01 on t(s01);
    create index t_s02 on t(s02);
    create index t_s03 on t(s03);
    create index t_s04 on t(s04);
    commit;

    delete from t;
    commit;
    quit;
"""

# 16K page is neccessary ! Smaller size will cause failure with:
# key size exceeds implementation restriction for index "T_S01"
#
db = db_factory(page_size=16384, init = init_sql)

act = python_act('db', substitutions = substitutions)

sweep_log = temp_file('tmp_4337_sweep.log')

trace = ['time_threshold = 0',
         'log_errors = true',
         'log_sweep = true',
         'log_connections = true',
         ]

@pytest.mark.trace
@pytest.mark.version('>=3.0')
def test_1(act: Action, sweep_log: Path, capsys):

    with act.connect_server() as srv:

        # REDUCE number of cache buffers in DB header in order to sweep make its work as long as possible
        srv.database.set_default_cache_size(database=act.db.db_path, size=75)

        # Change FW to ON (in order to make sweep life harder :))
        srv.database.set_write_mode(database=act.db.db_path, mode=DbWriteMode.SYNC)

        srv.info.get_log()
        log_before = srv.readlines()

    #---------------------------------------------------------------

    # How long can we wait (milliseconds) for the FIRST appearance of 'gfix' process in mon$attachments:
    #
    MAX_WAIT_FOR_SWEEP_START_MS = 3000

    # How long we wait (milliseconds) for SECOND appearance of 'gfix' process in mon$attachments, after it was killed.
    # NOTE. If it appears then we have a BUG
    MAX_WAIT_FOR_GFIX_RESTART_MS = 3000

    sweep_attach_id = None
    sweep_reconnect = None
    # Start trace
    with act.trace(db_events=trace):
        with act.db.connect() as con:
            f_sweep_log = open(sweep_log,'w')
            stm = r"select first 1 a.mon$attachment_id from mon$attachments a where a.mon$system_flag <> 1 and lower(a.mon$remote_process) similar to '(%[\\/](gfix|fbsvcmgr)(.exe)?)'"
            t1=py_dt.datetime.now()
            with con.cursor() as cur1:
                ps1 = cur1.prepare(stm)
                p_sweep = subprocess.Popen( [act.vars['gfix'], '-sweep', '-user', act.db.user, '-password', act.db.password, act.db.dsn],
                                            stdout = f_sweep_log,
                                            stderr = subprocess.STDOUT
                                          )

                ##########################################################################
                # LOOP-1: WAIT FOR FIRST APPEARANCE OF GFIX PROCESS IN THE MON$ATTACHMENTS
                ##########################################################################
                while True:
                    t2=py_dt.datetime.now()
                    d1=t2-t1
                    dd = d1.seconds*1000 + d1.microseconds//1000
                    if dd > MAX_WAIT_FOR_SWEEP_START_MS:
                        print(f'TIMEOUT EXPIRATION: waiting for SWEEP process took {dd} ms which exceeds limit = {MAX_WAIT_FOR_SWEEP_START_MS} ms.')
                        break

                    cur1.execute(ps1)
                    for r in cur1:
                        sweep_attach_id = r[0]
                    
                    con.commit()
                    if sweep_attach_id:
                        break
                    else:
                        time.sleep(0.1)
                #<while True (loop for search gfix process in mon$attachments)

            #< with con.cursor() as cur1

            #assert sweep_attach_id is None, f'attacment_id of SWEEP process is {sweep_attach_id}'
            assert sweep_attach_id, 'attacment_id of SWEEP process was not found.'

            # Let sweep to have some 'useful work':
            #
            time.sleep(1)

            # Now we can KILL attachment that belongs to SWEEP process, <sweep_attach_id>:
            con.execute_immediate(f'delete from mon$attachments where mon$attachment_id = {sweep_attach_id}')

            p_sweep.wait()
            f_sweep_log.close()

            assert p_sweep.returncode == 1, 'p_sweep.returncode: {p_sweep.returncode}'


            ##################################################################################################
            # LOOP-2: WAIT FOR POSSIBLE SECOND APPEARENCE (RECONNECT) OF GFIX. IF IT OCCURS THEN WE HAVE A BUG
            ##################################################################################################
            t1=py_dt.datetime.now()
            with con.cursor() as cur2:
                ps2 = cur2.prepare( stm.replace('select ', 'select /* search re-connect that could be made */ ') )
                while True:
                    t2=py_dt.datetime.now()
                    d1=t2-t1
                    dd = d1.seconds*1000 + d1.microseconds//1000
                    if dd > MAX_WAIT_FOR_GFIX_RESTART_MS:
                        # Expected: gfix reconnect was not detected for last {MAX_WAIT_FOR_GFIX_RESTART_MS} ms.
                        break
                    con.commit()
                    cur2.execute(ps2)
                    # Resultset now must be EMPTY. we must not find any record!
                    for r in cur2:
                        sweep_reconnect = r[0]
                    
                    #con.commit()
                    if sweep_reconnect:
                        # UNEXPECTED: gfix reconnect found, with attach_id={sweep_reconnect}
                        break
                    else:
                        time.sleep(0.1)
            #< with con.cursor() as cur2

            assert sweep_reconnect is None, f'Found re-connect of SWEEP process, attachment: {sweep_reconnect}'

        #< with db.connect as con

    #---------------------------------------------------------------
    # DISABLED 25.09.2022. SWEEP log can remain empty (4.0.1.2692 Classic)
    ## Check-1: log of sweep must contain text: 'connection shutdown':
    #for line in sweep_log.read_text().splitlines():
    #    if line:
    #        print('SWEEP LOG:', line.upper())
    #
    #act.expected_stdout = 'sweep log: connection shutdown'.upper()
    #act.stdout = capsys.readouterr().out
    #assert act.clean_stdout == act.clean_expected_stdout
    #act.reset()
    #---------------------------------------------------------------

    # Trace log
    found_sweep_failed = 0
    p_sweep_failed = re.compile( r'[.*\s+]*20\d{2}(-\d{2}){2}T\d{2}(:\d{2}){2}.\d{3,4}\s+\(.+\)\s+SWEEP_FAILED$', re.IGNORECASE)
    p_att_success = re.compile( r'[.*\s+]*20\d{2}(-\d{2}){2}T\d{2}(:\d{2}){2}.\d{3,4}\s+\(.+\)\s+ATTACH_DATABASE$', re.IGNORECASE)

    trace_expected = 'FOUND SWEEP_FAILED MESSAGE.'
    for i,line in enumerate(act.trace_log):
        if line.strip():
            if p_sweep_failed.search(line.strip()):
                print(trace_expected)
                found_sweep_failed = 1
            if found_sweep_failed == 1 and p_att_success.search(line) and i < len(act.trace_log)-2 and 'gfix' in act.trace_log[i+2].lower():
                # NB: we have to ignore "FAILED ATTACH_DATABASE".
                # It can occur in some cases.
                print('TRACE: UNEXPECTED ATTACH FOUND AFTER KILL SWEEP! CHECK LINE N {i}:')
                print('TRACE_LOG: ' + line)

    act.expected_stdout = trace_expected
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

    #----------------------------------------------------------------

    with act.connect_server() as srv:
        srv.info.get_log()
        log_after = srv.readlines()

    '''
    Example of diff:
    COMPUTERNAME	Wed Sep 14 15:58:37 2022
    	Sweep is started by SYSDBA
    	Database "C:/TEMP/PYTEST_PATH/TEST.FDB" 
    	OIT 20, OAT 21, OST 21, Next 21

    COMPUTERNAME	Wed Sep 14 15:58:37 2022
    	Error during sweep of C:/PYTEST_PATH/TEST.FDB:
    	connection shutdown
    '''

    p_tx_counter  = re.compile("\\+[\\s]+OIT[ ]+\\d+,[\\s]*OAT[\\s]+\\d+,[\\s]*OST[\\s]+\\d+,[\\s]*NEXT[\\s]+\\d+")
    for line in unified_diff(log_before, log_after):
        if line.startswith('+'):
            line = line.upper()
            if 'SWEEP' in line or 'CONNECTION' in line or p_tx_counter.match(line):
                print( 'FIREBIRD.LOG: ' + (' '.join(line.split())) )

    fb_log_expected = """
        FIREBIRD.LOG: + SWEEP IS STARTED BY SYSDBA
        FIREBIRD.LOG: + OIT, OAT, OST, NEXT
        FIREBIRD.LOG: + ERROR DURING SWEEP OF TEST.FDB
        FIREBIRD.LOG: + CONNECTION SHUTDOWN
    """

    act.expected_stdout = fb_log_expected
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
