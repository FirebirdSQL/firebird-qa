#coding:utf-8

"""
ID:          replication.shutdown_during_applying_segments_leads_to_crash
ISSUE:       6975
TITLE:       Crash or hang while shutting down the replica database if segments are being applied
DESCRIPTION:
    Bug initially was found during heavy test of replication performed by OLTP-EMUL, for FB 4.x
    (see letters to dimitr 13.09.2021; reply from dimitr, 18.09.2021 08:42 - all in mailbox: pz at ibase.ru).

    It *can* be reproduced without heavy/concurrent workload, but one need to make data be written into replica
    database 'slowly'. First of all, we have to set/change (temporary) Forced Writes = _ON_ for replica DB.
    Further, on master DB we can create table with wide INDEXED column and insert GUID-based values there.
    On master we have FW = OFF thus data will be inserted quickly, but on applying of segments to replica DB
    will be extremely slow (more than 1..2 minutes).

    At this point we save current timestamp and start to check replicationb.log for appearance of phrase
    'Added <N> segment(s) to the processing queue' - with requirement that this phrase has timestamp newer
    than just saved one (essentually, we are looking for LAST such phrase).
    See function wait_for_add_queue_in_replica() which does this parsing of replication.log.

    Since that point control is returned from func wait_for_add_queue_in_replica() to main code.
    We can be sure that replicating of segments will be performed very slow. In order to check ticket issue,
    we can now change replica DB to shutdown - and FB must not chash at this point.

    We also have to return FW state to 'OFF', so before shutting down this DB we change it FW attribute
    (see 'srv.database.set_write_mode(...)').
    NOTE: changing FW attribute causes error on 5.0.0.215 with messages:
        335544344 : I/O error during "WriteFile" operation for file "<db_repl_file.fdb>"
        335544737 : Error while trying to write to file
    - so we have to enclose it into try/except block (otherwise we will not see crash because of test terminating).

    When we further change DB replica state to full shutdown, FB 5.0.0.215 crashes (checked both of SS and CS).
    After returning DB to online ('srv.database.bring_online'), we will wait for all segments will be applied.
    If this occurs then we can conclude that test passes.

    Finally, we extract metadata for master and replica and compare them (see 'f_meta_diff').
    The only difference in metadata must be 'CREATE DATABASE' statement with different DB names - we suppress it,
    thus metadata difference must not be issued.


    Confirmed bug on 5.0.0.215: server crashed when segment was applied to replica and at the same time we issued
    'gfix -shut full -force 0 ...'. Regardless of that command, replica DB remained in NORMAL mode, not in shutdown.
    If this command was issued after this again - FB process hanged (gfix could not return control to OS).
    This is the same bug as described in the ticked (discussed with dimitr, letters 22.09.2021).

FBTEST:      tests.functional.replication.shutdown_during_applying_segments_leads_to_crash
NOTES:
    [27.08.2022] pzotov
    1. In case of any errors (somewhat_failed <> 0) test will re-create db_main and db_repl, and then perform all needed
       actions to resume replication (set 'replica' flag on db_repl, enabling publishing in db_main, remove all files
       from subdirectories <repl_journal> and <repl_archive> which must present in the same folder as <db_main>).
    2. Warning raises on Windows and Linux:
       ../../../usr/local/lib/python3.9/site-packages/_pytest/config/__init__.py:1126
          /usr/local/lib/python3.9/site-packages/_pytest/config/__init__.py:1126: 
          PytestAssertRewriteWarning: Module already imported so cannot be rewritten: __editable___firebird_qa_0_17_0_finder
            self._mark_plugins_for_rewrite(hook)
       The reason currently is unknown.

	3. Following message appears in the firebird.log during this test:
	    3.1.[WINDOWS] 
        I/O error during "WriteFile" operation for file "<db_replica_filename>"
        Error while trying to write to file

        3.2 [LINUX]
        I/O error during "write" operation for file "<db_replica_filename>"
        Error while trying to write to file
        Success
    
    4. ### ACHTUNG ###
       On linux test atually "silently" FAILS, without showing any error (but FB process is terminated!).
       Will be investigated later.

    Checked on 5.0.0.691, 4.0.1.2692 - both CS and SS. Both on Windows and Linux.
"""
import os
import shutil
import re
from difflib import unified_diff
from pathlib import Path
import time
from datetime import datetime
from datetime import timedelta

import pytest
from firebird.qa import *
from firebird.driver import connect, create_database, DbWriteMode, ReplicaMode, ShutdownMode,ShutdownMethod, OnlineMode
from firebird.driver.types import DatabaseError

# QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
# from act.files_dir/'test_config.ini':
repl_settings = QA_GLOBALS['replication']

MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG = int(repl_settings['max_time_for_wait_segment_in_log'])
MAX_TIME_FOR_WAIT_ADDED_TO_QUEUE = int(repl_settings['max_time_for_wait_added_to_queue'])

MAIN_DB_ALIAS = repl_settings['main_db_alias']
REPL_DB_ALIAS = repl_settings['repl_db_alias']

db_main = db_factory( filename = '#' + MAIN_DB_ALIAS, do_not_create = True, do_not_drop = True)
db_repl = db_factory( filename = '#' + REPL_DB_ALIAS, do_not_create = True, do_not_drop = True)

substitutions = [('Start removing objects in:.*', 'Start removing objects'),
                 ('Finish. Total objects removed:  [1-9]\\d*', 'Finish. Total objects removed'),
                 ('.* CREATE DATABASE .*', ''),
                 ('[\t ]+', ' '),
                 ('FOUND message about replicated segment N .*', 'FOUND message about replicated segment'),
                 ('FOUND message about segments added to queue after timestamp .*', 'FOUND message about segments added to queue after timestamp')
                ]

act_db_main = python_act('db_main', substitutions=substitutions)
act_db_repl = python_act('db_repl', substitutions=substitutions)

#--------------------------------------------

def cleanup_folder(p):
    # Removed all files and subdirs in the folder <p>
    # Used for cleanup <repl_journal> and <repl_archive> when replication must be reset
    # in case when any error occurred during test execution.
    assert os.path.dirname(p) != p, f"@@@ ABEND @@@ CAN NOT operate in the file system root directory. Check your code!"
    for root, dirs, files in os.walk(p):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    return len(os.listdir(p))

#--------------------------------------------

def wait_for_add_queue_in_replica( act_db_main: Action, max_allowed_time_for_wait, min_timestamp, prefix_msg = '' ):

    # <hostname> (replica) Tue Sep 21 20:24:57 2021
    # Database: ...
    # Added 3 segment(s) to the processing queue

    # -:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-
    def check_pattern_in_log( log_lines, pattern, min_timestamp, prefix_msg = '' ):
        found_required_message = False
        for i,r in enumerate(log_lines):
            if pattern.search(r):
                if i>=2 and log_lines[i-2]:
                    # a = r.replace('(',' ').split()
                    a = log_lines[i-2].split()
                    if len(a)>=4:
                        # s='replica_host_name (slave) Sun May 30 17:46:43 2021'
                        # s.split()[-5:] ==> ['Sun', 'May', '30', '17:46:43', '2021']
                        # ' '.join( ...) ==> 'Sun May 30 17:46:43 2021'
                        dts = ' '.join( log_lines[i-2].split()[-5:] )
                        segment_timestamp = datetime.strptime( dts, '%a %b %d %H:%M:%S %Y')
                        if segment_timestamp >= min_timestamp:
                            print( (prefix_msg + ' ' if prefix_msg else '') + f'FOUND message about segments added to queue after timestamp {min_timestamp}: {segment_timestamp}')
                            found_required_message = True
                            break
        return found_required_message

    # -:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-

    replication_log = act_db_main.home_dir / 'replication.log'

    replold_lines = []
    with open(replication_log, 'r') as f:
        replold_lines = f.readlines()


    # VERBOSE: Added 5 segment(s) to the processing queue
    segments_to_queue_pattern=re.compile( 'VERBOSE:\\s+added\\s+\\d+\\s+segment.*to.*queue', re.IGNORECASE)

    # 08.09.2021: replication content can already contain phrase which we are looking for.
    # Because of this, it is crucial to check OLD content of replication log before loop.
    # Also, segments_to_queue_pattern must NOT start from '\\+' because it can occur only for diff_data (within loop):
    #
    found_required_message = check_pattern_in_log( replold_lines, segments_to_queue_pattern, min_timestamp, prefix_msg )

    if not found_required_message:
        for i in range(0,max_allowed_time_for_wait):
            time.sleep(1)
            # Get content of fb_home replication.log _after_ isql finish:
            with open(replication_log, 'r') as f:
                diff_data = unified_diff(
                    replold_lines,
                    f.readlines()
                  )

            found_required_message = check_pattern_in_log( list(diff_data), segments_to_queue_pattern, min_timestamp, prefix_msg )
            if found_required_message:
                break

    if not found_required_message:
        print(f'UNEXPECTED RESULT: no message about segments added to queue after {min_timestamp}.')

#--------------------------------------------

def wait_for_data_in_replica( act_db_main: Action, max_allowed_time_for_wait, prefix_msg = '' ):

    replication_log = act_db_main.home_dir / 'replication.log'

    replold_lines = []
    with open(replication_log, 'r') as f:
        replold_lines = f.readlines()

    with act_db_main.db.connect(no_db_triggers = True) as con:
        with con.cursor() as cur:
            cur.execute("select rdb$get_context('SYSTEM','REPLICATION_SEQUENCE') from rdb$database")
            last_generated_repl_segment = cur.fetchone()[0]

    # VERBOSE: Segment 1 (2582 bytes) is replicated in 1 second(s), deleting the file
    # VERBOSE: Segment 2 (200 bytes) is replicated in 82 ms, deleting the file
    p_successfully_replicated = re.compile( f'\\+\\s+verbose:\\s+segment\\s+{last_generated_repl_segment}\\s+\\(\\d+\\s+bytes\\)\\s+is\\s+replicated.*deleting', re.IGNORECASE)

    # VERBOSE: Segment 16 replication failure at offset 33628
    p_replication_failure = re.compile('segment\\s+\\d+\\s+replication\\s+failure', re.IGNORECASE)

    found_required_message = False
    found_replfail_message = False
    found_common_error_msg = False

    for i in range(0,max_allowed_time_for_wait):

        time.sleep(1)

        # Get content of fb_home replication.log _after_ isql finish:
        with open(replication_log, 'r') as f:
            diff_data = unified_diff(
                replold_lines,
                f.readlines()
              )

        for k,d in enumerate(diff_data):
            if p_successfully_replicated.search(d):
                # We FOUND phrase "VERBOSE: Segment <last_generated_repl_segment> ... is replicated ..." in the replication log.
                # This is expected success, break!
                print( (prefix_msg + ' ' if prefix_msg else '') + f'FOUND message about replicated segment N {last_generated_repl_segment}.' )
                found_required_message = True
                break

            if p_replication_failure.search(d):
                print( (prefix_msg + ' ' if prefix_msg else '') + '@@@ SEGMENT REPLICATION FAILURE @@@ ' + d )
                found_replfail_message = True
                break

            if 'ERROR:' in d:
                print( (prefix_msg + ' ' if prefix_msg else '') + '@@@ REPLICATION ERROR @@@ ' + d )
                found_common_error_msg = True
                break

        if found_required_message or found_replfail_message or found_common_error_msg:
            break

    if not found_required_message:
        print(f'UNEXPECTED RESULT: no message about replicating segment N {last_generated_repl_segment} for {max_allowed_time_for_wait} seconds.')

#--------------------------------------------

@pytest.mark.version('>=4.0.1')
def test_1(act_db_main: Action,  act_db_repl: Action, capsys):

    #assert '' == capsys.readouterr().out

    ###################
    somewhat_failed = 1
    ###################
    try:

        N_ROWS = 30000
        FLD_WIDTH = 700

        # N_ROWS = 30'000:
        #     FW = ON ==>
        #         Added 2 segment(s) to the processing queue
        #         Segment 1 (16783004 bytes) is replicated in 1 minute(s), preserving the file due to 1 active transaction(s) (oldest: 10 in segment 1)
        #         Segment 2 (4667696 bytes) is replicated in 55 second(s), deleting the file
        #     FW = OFF ==>
    	#         Segment 1 (16783004 bytes) is replicated in 1 second(s), preserving the file due to 1 active transaction(s) (oldest: 10 in segment 1)
    	#         Segment 2 (4667696 bytes) is replicated in 374 ms, deleting the file

        act_db_main.db.set_async_write()
        act_db_repl.db.set_sync_write()
        assert '' == capsys.readouterr().out

        current_date_with_hhmmss = datetime.today().replace(microsecond=0) # datetime.datetime(2022, 8, 26, 22, 54, 33) etc

        sql_init = f'''
            set bail on;
            recreate table test(s varchar({FLD_WIDTH}), constraint test_s_unq unique(s));
            commit;

            set term ^;
            execute block as
                declare fld_len int;
                declare n int;
            begin
                select ff.rdb$field_length
                from rdb$relation_fields rf
                join rdb$fields ff on rf.rdb$field_source = ff.rdb$field_name
                where upper(rf.rdb$relation_name) = upper('test') and upper(rf.rdb$field_name) = upper('s')
                into fld_len;


                n = {N_ROWS};
                while (n > 0) do
                begin
                    insert into test(s) values( lpad('', :fld_len, uuid_to_char(gen_uuid())) );
                    n = n - 1;
                end

            end
            ^
            set term ;^
            commit;
        '''

        act_db_main.expected_stderr = ''
        act_db_main.isql(switches=['-q'], input = sql_init)
        assert act_db_main.clean_stderr == act_db_main.clean_expected_stderr
        act_db_main.reset()

        act_db_main.expected_stdout = f'POINT-1 FOUND message about segments added to queue after timestamp {current_date_with_hhmmss}'
        ##############################################################################
        ###  W A I T   F O R    S E G M E N T S    A D D E D    T O    Q U E U E   ###
        ##############################################################################
        wait_for_add_queue_in_replica( act_db_main, MAX_TIME_FOR_WAIT_ADDED_TO_QUEUE, current_date_with_hhmmss, 'POINT-1' )

        act_db_main.stdout = capsys.readouterr().out
        assert act_db_main.clean_stdout == act_db_main.clean_expected_stdout
        act_db_main.reset()

        time.sleep(1)

        with act_db_repl.connect_server() as srv:

            try:
                # 5.0.0.215:
                # 335544344 : I/O error during "WriteFile" operation for file "<db_repl_file.fdb>"
                # 335544737 : Error while trying to write to file
                srv.database.set_write_mode(database=act_db_repl.db.db_path
                                            , mode=DbWriteMode.ASYNC
                                           )
            except:
                pass

            #try:
            # 5.0.0.215:
            # FB crashes here, replication archive folder can not be cleaned:
            # PermissionError: [WinError 32] ...: '<repl_arc_sub_dir>/<dbmain>.journal-NNN'
            srv.database.shutdown(
                                      database=act_db_repl.db.db_path
                                      ,mode=ShutdownMode.FULL
                                      ,method=ShutdownMethod.FORCED
                                      ,timeout=0
                                 )
            
            # Without crash replication here will be resumed, but DB_REPL now has FW = OFF, and segments
            # will be replicated very fast after this:
            srv.database.bring_online(
                                      database=act_db_repl.db.db_path
                                      ,mode=OnlineMode.NORMAL
                                     )

        assert '' == capsys.readouterr().out
        
        act_db_main.expected_stdout = 'POINT-2 FOUND message about replicated segment'
        ##############################################################################
        ###  W A I T   U N T I L    R E P L I C A    B E C O M E S   A C T U A L   ###
        ##############################################################################
        wait_for_data_in_replica( act_db_main, MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG, 'POINT-2' )
        
        act_db_main.stdout = capsys.readouterr().out
        assert act_db_main.clean_stdout == act_db_main.clean_expected_stdout
        act_db_main.reset()


        #---------------------------------------------------

        # return initial state of master DB:
        # remove all DB objects (tables, views, ...):
        #
        db_main_meta, db_repl_meta = '', ''
        for a in (act_db_main,act_db_repl):
            if a == act_db_main:
                sql_clean = (a.files_dir / 'drop-all-db-objects.sql').read_text()
                a.expected_stdout = """
                    Start removing objects
                    Finish. Total objects removed
                """
                a.isql(switches=['-q', '-nod'], input = sql_clean, combine_output = True)
                assert a.clean_stdout == a.clean_expected_stdout
                a.reset()

                
                a.expected_stdout = 'POINT-3 FOUND message about replicated segment'
                ##############################################################################
                ###  W A I T   U N T I L    R E P L I C A    B E C O M E S   A C T U A L   ###
                ##############################################################################
                wait_for_data_in_replica( a, MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG, 'POINT-3' )

                a.stdout = capsys.readouterr().out
                assert a.clean_stdout == a.clean_expected_stdout
                a.reset()

                db_main_meta = a.extract_meta(charset = 'utf8', io_enc = 'utf8')
            else:
                db_repl_meta = a.extract_meta(charset = 'utf8', io_enc = 'utf8')

            ######################
            ### A C H T U N G  ###
            ######################
            # MANDATORY, OTHERWISE REPLICATION GETS STUCK ON SECOND RUN OF THIS TEST
            # WITH 'ERROR: Record format with length NN is not found for table TEST':
            a.gfix(switches=['-sweep', a.db.dsn])


        # Final point: metadata must become equal:
        #
        diff_meta = ''.join(unified_diff( \
                             [x for x in db_main_meta.splitlines() if 'CREATE DATABASE' not in x],
                             [x for x in db_repl_meta.splitlines() if 'CREATE DATABASE' not in x])
                           )
        assert diff_meta == ''

        
        ###################
        somewhat_failed = 0
        ###################
    
    except Exception as e:
        print(e.__str__())

    finally:
        if somewhat_failed:
            # If any previous assert failed, we have to RECREATE both master and slave databases.
            # Otherwise further execution of this test or other replication-related tests most likely will fail.
            for a in (act_db_main,act_db_repl):
                d = a.db.db_path
                a.db.drop()
                dbx = create_database(str(d), user = a.db.user)
                dbx.close()
                with a.connect_server() as srv:
                    srv.database.set_write_mode(database = d, mode=DbWriteMode.ASYNC)
                    srv.database.set_sweep_interval(database = d, interval = 0)
                    if a == act_db_repl:
                        srv.database.set_replica_mode(database = d, mode = ReplicaMode.READ_ONLY)
                    else:
                        with a.db.connect() as con:
                            # !! IT IS ASSUMED THAT REPLICATION FOLDERS ARE IN THE SAME DIR AS <DB_MAIN> !!
                            # DO NOT use 'a.db.db_path' for ALIASED database!
                            # Its '.parent' property will be '.' rather than full path.
                            # Use only con.info.name for that:
                            repl_root_path = Path(con.info.name).parent
                            repl_jrn_sub_dir = repl_settings['journal_sub_dir']
                            repl_arc_sub_dir = repl_settings['archive_sub_dir']

                            # Clean folders repl_journal and repl_archive (remove all files from there):
                            for p in (repl_jrn_sub_dir,repl_arc_sub_dir):
                                # PermissionError: [WinError 32] ...: '<repl_arc_sub_dir>/<dbmain>.journal-000000001'
                                assert cleanup_folder(repl_root_path / p) == 0, f"Directory {str(p)} remains non-empty."

                            con.execute_immediate('alter database enable publication')
                            con.execute_immediate('alter database include all to publication')
                            con.commit()
            assert '' == capsys.readouterr().out
