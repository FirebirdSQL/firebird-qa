#coding:utf-8

"""
ID:          issue-1535
ISSUE:       1535
TITLE:       gfix -sweep makes "reconnect" when it is removed from mon$attachments by delete command (issued in another window)
DESCRIPTION:
    We create table with very long char field and fill it with uuid data.
    Then we create index for this field and finally - delete all rows.
    Such table will require valuable time to be swept, about 4 seconds.

    After this, we launch asynchronously ISQL which makes delay ~2 seconds inside itself.
    Also, we launch trace for logging.

    After this we run 'gfix -sweep' in another process (synchronously).
    When delay in ISQL expires, ISQL connection executes 'DELETE FROM MON$ATTACHMENT' command
    which should kill gfix connection. This command is issued with 'set count on' for additional
    check that isql really could find this record in momn$attachments table.

    Process of GFIX should raise error 'connection shutdown'.
    Trace log should contain line with text 'SWEEP_FAILED' and after this line we should NOT
    discover any lines with 'ATTACH_DATABASE' event - this is especially verified.

    Finally, we compare content of firebird.log: new lines in it should contain messages about
    interrupted sweep ('error during sweep' and 'connection shutdown').

    Checked on WI-V3.0.2.32620 (SS/SC/CS), 4.0.0.420 (SS/SC).
    Total time of test run is ~25 seconds (data filling occupies about 3 seconds).
NOTES:
[11.05.2017] checked on WI-T4.0.0.638 - added filtering to messages about shutdown state, see comments below.
[26.09.2017]
  adjusted expected_stdout section to current FB 3.0+ versions: firebird.log now does contain info
  about DB name which was swept (see CORE-5610, "Provide info about database (or alias) which was in use...")
[19.11.2021] pcisar
  Small difference in reimplementation of sweep killer script
  On v4.0.0.2496 COMMIT after delete from mon#attachments fails with:
  STATEMENT FAILED, SQLSTATE = HY008, OPERATION WAS CANCELLED
  Without commit this test PASSES, i.e. sweep is terminated with all outputs as expected
JIRA:        CORE-4337
FBTEST:      bugs.core_4337
"""

import pytest
import re
import time
import subprocess
from difflib import unified_diff
from pathlib import Path
from firebird.qa import *
from firebird.driver import DbWriteMode

substitutions = [('[ ]+', ' '), ('TRACE_LOG:.* SWEEP_START', 'TRACE_LOG: SWEEP_START'),
                 ('TRACE_LOG:.* SWEEP_FAILED', 'TRACE_LOG: SWEEP_FAILED'),
                 ('TRACE_LOG:.* ERROR AT JPROVIDER::ATTACHDATABASE',
                  'TRACE_LOG: ERROR AT JPROVIDER::ATTACHDATABASE'),
                 ('.*KILLED BY DATABASE ADMINISTRATOR.*', ''),
                 ('TRACE_LOG:.*GFIX.EXE.*', 'TRACE_LOG: GFIX.EXE'),
                 ('OIT [0-9]+', 'OIT'), ('OAT [0-9]+', 'OAT'), ('OST [0-9]+', 'OST'),
                 ('NEXT [0-9]+', 'NEXT'),
                 ('FIREBIRD.LOG:.* ERROR DURING SWEEP OF .*TEST.FDB.*',
                  'FIREBIRD.LOG: + ERROR DURING SWEEP OF TEST.FDB')]

# 16K page is neccessary ! Smaller size will cause failure with:
# key size exceeds implementation restriction for index "T_S01"
db = db_factory(page_size=16384)

act = python_act('db', substitutions=substitutions)

make_garbage = """
    set list on;
    select current_time from rdb$database;
    recreate table t(s01 varchar(4000));
    commit;
    set term ^;
    execute block as
        declare n int = 20000;
        declare w int;
    begin
        select f.rdb$field_length
        from rdb$relation_fields rf
        join rdb$fields f on rf.rdb$field_source=f.rdb$field_name
        where rf.rdb$relation_name=upper('t')
        into w;

        while (n>0) do
            insert into t(s01) values( rpad('', :w, uuid_to_char(gen_uuid())) ) returning :n-1 into n;
    end^
    set term ;^
    commit;
    select count(*) check_total_cnt, min(char_length(s01)) check_min_length from t;

    create index t_s01 on t(s01);
    commit;

    delete from t;
    commit;
    -- overall time for data filling , create index and delete all rows: ~ 3 seconds.
    -- This database requires about 4 seconds to be swept (checked on P-IV 3.0 GHz).
    select current_time from rdb$database;
    --show database;
    quit;
"""

expected_stdout = """
    CONNECTION SHUTDOWN
    ISQL LOG: WAITING FOR GFIX START SWEEP
    ISQL LOG: STARTING TO DELETE GFIX PROCESS FROM MON$ATTACHMENTS
    ISQL LOG: RECORDS AFFECTED: 1
    ISQL LOG: FINISHED DELETING GFIX PROCESS FROM MON$ATTACHMENTS
    TRACE_LOG: SWEEP_FAILED
    FIREBIRD.LOG: + SWEEP IS STARTED BY SYSDBA
    FIREBIRD.LOG: + OIT, OAT, OST, NEXT
    FIREBIRD.LOG: + ERROR DURING SWEEP OF TEST.FDB
    FIREBIRD.LOG: + CONNECTION SHUTDOWN
"""

killer_script = """
    set list on;

    recreate table tmp4wait(id int);
    commit;
    insert into tmp4wait(id) values(1);
    commit;

    set transaction lock timeout 2; ------------------  D E L A Y
    update tmp4wait set id=id;
    select 'Waiting for GFIX start SWEEP' as " " from rdb$database;
    set term ^;
    execute block as
    begin
       in autonomous transaction do
       begin
           update tmp4wait set id=id;
           when any do
           begin
              -- NOP --
           end
       end
    end
    ^
    set term ;^
    commit;
    --select MON$PAGE_BUFFERS from mon$database;
    select 'Starting to delete GFIX process from mon$attachments' as " " from rdb$database;
    set count on;
    delete from mon$attachments where mon$remote_process containing 'gfix';
    -- On v4.0.0.2496 COMMIT fails with: STATEMENT FAILED, SQLSTATE = HY008, OPERATION WAS CANCELLED
    -- Without commit this test PASSES, i.e. sweep is terminated with all outputs as expected
    -- commit;
    set count off;
    select 'Finished deleting GFIX process from mon$attachments' as " " from rdb$database;
"""

killer_script_file = temp_file('killer.sql')
sweep_killer_out = temp_file('killer.out')
sweep_killer_err = temp_file('killer.err')
sweep_out = temp_file('sweep.out')

trace = ['time_threshold = 0',
         'log_errors = true',
         'log_sweep = true',
         'log_connections = true',
         ]

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys, killer_script_file: Path, sweep_killer_out: Path,
           sweep_killer_err: Path, sweep_out: Path):
    killer_script_file.write_text(killer_script)
    with act.connect_server() as srv:
        # get firebird log before action
        srv.info.get_log()
        log_before = srv.readlines()
        # Change FW to OFF in order to speed up initial data filling
        srv.database.set_write_mode(database=act.db.db_path, mode=DbWriteMode.ASYNC)
        # make garbage
        act.isql(switches=[], input=make_garbage)
        # REDUCE number of cache buffers in DB header in order to sweep make its work as long as possible
        srv.database.set_default_cache_size(database=act.db.db_path, size=100)
        # Change FW to ON (in order to make sweep life harder :))
        srv.database.set_write_mode(database=act.db.db_path, mode=DbWriteMode.SYNC)
    # Start trace
    with act.trace(db_events=trace):
        # Launch (async.) ISQL which will make small delay and then kill GFIX attachment
        with open(sweep_killer_out, 'w') as killer_out, \
             open(sweep_killer_err, 'w') as killer_err:
            p_killer = subprocess.Popen([act.vars['isql'],
                                            '-i', str(killer_script_file),
                                           '-user', act.db.user,
                                           '-password', act.db.password, act.db.dsn],
                                           stdout=killer_out, stderr=killer_err)
            try:
                time.sleep(2)
                # Launch GFIX -SWEEP (sync.). It should be killed by ISQL which we have
                # launched previously after delay in its script will expire:
                act.expected_stderr = 'We expect errors'
                act.gfix(switches=['-sweep', act.db.dsn])
                gfix_out = act.stdout
                gfix_err = act.stderr
            finally:
                p_killer.terminate()
    #
    # get firebird log after action
    with act.connect_server() as srv:
        srv.info.get_log()
        log_after = srv.readlines()
    # construct final stdout for checks
    print(gfix_out.upper())
    print(gfix_err.upper())
    # sweep filler output
    for line in sweep_killer_out.read_text().splitlines():
        if line:
            print('ISQL LOG:', line.upper())
    for line in sweep_killer_err.read_text().splitlines():
        if line:
            print('ISQL ERR:', line.upper())
    # Trace log
    found_sweep_failed = 0
    for line in act.trace_log:
        if 'SWEEP_FAILED' in line:
            print('TRACE_LOG:' + (' '.join(line.split()).upper()))
            found_sweep_failed = 1
        if found_sweep_failed == 1 and ('ATTACH_DATABASE' in line):
            print('TRACE: ATTACH DETECTED AFTER SWEEP FAILED! ')
            print('TRACE_LOG:' + (' '.join(line.split()).upper()))
    #
    pattern  = re.compile("\\+[\\s]+OIT[ ]+[0-9]+,[\\s]*OAT[\\s]+[0-9]+,[\\s]*OST[\\s]+[0-9]+,[\\s]*NEXT[\\s]+[0-9]+")
    for line in unified_diff(log_before, log_after):
        if line.startswith('+'):
            line = line.upper()
            if 'SWEEP' in line or 'CONNECTION' in line or pattern.match(line):
                print( 'FIREBIRD.LOG: ' + (' '.join(line.split())) )
    #
    # check
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
