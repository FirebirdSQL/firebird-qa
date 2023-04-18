#coding:utf-8

"""
ID:          replication.shutdown_during_applying_segments_leads_to_crash
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/6975
TITLE:       Crash or hang while shutting down the replica database if segments are being applied
DESCRIPTION:
    Bug initially was found during heavy test of replication performed by OLTP-EMUL, for FB 4.x
    (see letters to dimitr 13.09.2021; reply from dimitr, 18.09.2021 08:42 - all in mailbox: pz at ibase.ru).

    It *can* be reproduced without heavy/concurrent workload, but one need to make data be written into replica
    database 'slowly'. First of all, we have to set/change (temporary) Forced Writes = _ON_ for replica DB.
    Further, on master DB we can create table with wide INDEXED column and insert GUID-based values there.
    On master we have FW = OFF thus data will be inserted quickly, but applying of segments to replica DB
    will be extremely slow (about 1..2 minutes).

    Test creates table 'test' with indexed text column of length about 500...700 bytes, and adds there thousands rows.
    This leads engine generate at least one segment with size about 16 Mb.

    We wait until table 'test' appear in replica DB (by querying RDB$RELATIONS), and when it is so - make small delay
    for <TIME_TO_LET_SEGMENTS_BE_APPLIED> seconds in order to allow replica apply some (small) part of this big segment.
    After that, we change replica DB state to 'full shutdown' and then bring it online.
    
    Error message appears in replication.log at that moment, engine suspends replication for <REPLICA_TIMEOUT_FOR_ERROR> seconds.
    After that, replication must resume and complete normally. We check this by querying RDB$RELATIONS for presense there table
    with name 't_completed': if appropriate record found then we can assume that replication completed successfully.

    Further, we invoke ISQL with executing auxiliary script for drop all DB objects on master (with '-nod' command switch).
    After all objects will be dropped, we have to wait again until replica becomes actual with master.
    Check that both DB have no custom objects is performed (see UNION-ed query to rdb$ tables + filtering on rdb$system_flag).

    Finally, we extract metadata for master and replica and make comparison.
    The only difference in metadata must be 'CREATE DATABASE' statement with different DB names - we suppress it,
    thus metadata difference must not be issued.
    
    Confirmed bug on 5.0.0.215: server crashed, firebird.log contains message:
    "Fatal lock manager error: invalid lock id (0), errno: 0".
    Validation of replica DB shows lot of orphan pages (but no errors).
    
    This is the same bug as described in the ticked (discussed with dimitr, letters 22.09.2021).

FBTEST:      tests.functional.replication.shutdown_during_applying_segments_leads_to_crash
NOTES:
    [27.08.2022] pzotov
    Warning raises on Windows and Linux:
        ../../../usr/local/lib/python3.9/site-packages/_pytest/config/__init__.py:1126
        /usr/local/lib/python3.9/site-packages/_pytest/config/__init__.py:1126: 
        PytestAssertRewriteWarning: Module already imported so cannot be rewritten: __editable___firebird_qa_0_17_0_finder
        self._mark_plugins_for_rewrite(hook)
    The reason currently is unknown.

    [18.04.2023] pzotov
    Test was fully re-implemented. We have to query replica DATABASE for presense of data that we know there must appear.
    We have to avoid query of replication log - not only verbose can be disabled, but also because code is too complex.

    NOTE-1.
        We use 'assert' only at the final point of test, with printing detalization about encountered problem(s).
        During all previous steps, we only store unexpected output to variables, e.g.: out_main = capsys.readouterr().out etc.
    NOTE-2.
        Temporary DISABLED execution on Linux when ServerMode = Classic. Replication can unexpectedly stop with message
        'Engine is shutdown' appears in replication.log. Sent report to dimitr, waiting for fix.
    
    Checked on 5.0.0.1017, 4.0.3.2925 - both SS and CS.
"""
import os
import shutil
from difflib import unified_diff
from pathlib import Path
import time

import pytest
from firebird.qa import *
from firebird.driver import connect, create_database, DbWriteMode, ReplicaMode, ShutdownMode, ShutdownMethod, OnlineMode, DatabaseError
from firebird.driver.types import DatabaseError

# QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
# from act.files_dir/'test_config.ini':
repl_settings = QA_GLOBALS['replication']

MAX_TIME_FOR_WAIT_DATA_IN_REPLICA = int(repl_settings['max_time_for_wait_data_in_replica'])

# How long we wit since segments start apply on replica
# and before we change its state to full shutdown, seconds:
#
TIME_TO_LET_SEGMENTS_BE_APPLIED = 5

# How long engine will be idle in case of encountering error.
#
REPLICA_TIMEOUT_FOR_ERROR = int(repl_settings['replica_timeout_for_error'])

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

def reset_replication(act_db_main, act_db_repl, db_main_file, db_repl_file):
    out_reset = ''

    with act_db_main.connect_server() as srv:

        # !! IT IS ASSUMED THAT REPLICATION FOLDERS ARE IN THE SAME DIR AS <DB_MAIN> !!
        # DO NOT use 'a.db.db_path' for ALIASED database!
        # It will return '.' rather than full path+filename.

        repl_root_path = Path(db_main_file).parent
        repl_jrn_sub_dir = repl_settings['journal_sub_dir']
        repl_arc_sub_dir = repl_settings['archive_sub_dir']

        for f in (db_main_file, db_repl_file):
            # Method db.drop() changes LINGER to 0, issues 'delete from mon$att' with suppressing exceptions
            # and calls 'db.drop_database()' (also with suppressing exceptions).
            # We change DB state to FULL SHUTDOWN instead of call action.db.drop() because
            # this is more reliable (it kills all attachments in all known cases and does not use mon$ table)
            #
            try:
                srv.database.shutdown(database = f, mode = ShutdownMode.FULL, method = ShutdownMethod.FORCED, timeout = 0)
            except DatabaseError as e:
                out_reset += e.__str__()

            # REMOVE db file from disk:
            ###########################
            os.unlink(f)

        # Clean folders repl_journal and repl_archive: remove all files from there.
        for p in (repl_jrn_sub_dir,repl_arc_sub_dir):
            if cleanup_folder(repl_root_path / p) > 0:
                out_reset += f"Directory {str(p)} remains non-empty.\n"

    if out_reset == '':
        for a in (act_db_main,act_db_repl):
            d = a.db.db_path

            try:
                dbx = create_database(str(d), user = a.db.user)
                dbx.close()
                with a.connect_server() as srv:
                    srv.database.set_write_mode(database = d, mode = DbWriteMode.ASYNC)
                    srv.database.set_sweep_interval(database = d, interval = 0)
                    if a == act_db_repl:
                        srv.database.set_replica_mode(database = d, mode = ReplicaMode.READ_ONLY)
                    else:
                        with a.db.connect() as con:
                            con.execute_immediate('alter database enable publication')
                            con.execute_immediate('alter database include all to publication')
                            con.commit()
            except DatabaseError as e:
                out_reset += e.__str__()
            
    # Must remain EMPTY:
    return out_reset

#--------------------------------------------

def watch_replica( a: Action, max_allowed_time_for_wait, ddl_ready_query = '', isql_check_script = '', replica_expected_out = ''):

    retcode = 1;
    ready_to_check = False
    if ddl_ready_query:
        with a.db.connect(no_db_triggers = True) as con:
            with con.cursor() as cur:
                for i in range(0,max_allowed_time_for_wait):
                    cur.execute(ddl_ready_query)
                    count_actual = cur.fetchone()
                    if count_actual:
                        ready_to_check = True
                        break
                    else:
                        con.rollback()
                        time.sleep(1)
    else:
        ready_to_check = True

    if not ready_to_check:
        print( f'UNEXPECTED. Initial check query did not return any rows for {max_allowed_time_for_wait} seconds.' )
        print('Initial check query:')
        print(ddl_ready_query)
        return
    
    final_check_pass = False
    if isql_check_script:
        retcode = 0
        for i in range(max_allowed_time_for_wait):
            a.reset()
            a.expected_stdout = replica_expected_out
            a.isql(switches=['-q', '-nod'], input = isql_check_script, combine_output = True)

            if a.return_code:
                # "Token unknown", "Name longer than database column size" etc: we have to
                # immediately break from this loop because isql_check_script is incorrect!
                break
            
            if a.clean_stdout == a.clean_expected_stdout:
                final_check_pass = True
                break
            if i < max_allowed_time_for_wait-1:
                time.sleep(1)

        if not final_check_pass:
            print(f'UNEXPECTED. Final check query did not return expected dataset for {max_allowed_time_for_wait} seconds.')
            print('Final check query:')
            print(isql_check_script)
            print('Expected output:')
            print(a.clean_expected_stdout)
            print('Actual output:')
            print(a.clean_stdout)
            print(f'ISQL return_code={a.return_code}')
            print(f'Waited for {i} seconds')

        a.reset()

    else:
        final_check_pass = True

    return

#--------------------------------------------

def drop_db_objects(act_db_main: Action,  act_db_repl: Action, capsys):

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
            if a.clean_stdout == a.clean_expected_stdout:
                a.reset()
            else:
                print(a.clean_expected_stdout)
                a.reset()
                break

            # NB: one need to remember that rdb$system_flag can be NOT ONLY 1 for system used objects!
            # For example, it has value =3 for triggers that are created to provide CHECK-constraints,
            # Custom DB objects always have rdb$system_flag = 0 (or null for some very old databases).
            # We can be sure that there are no custom DB objects if following query result is NON empty:
            #
            ddl_ready_query = """
                select 1
                from rdb$database
                where NOT exists (
                    select custom_db_object_flag
                    from (
                        select rt.rdb$system_flag as custom_db_object_flag from rdb$triggers rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$relations rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$functions rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$procedures rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$exceptions rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$fields rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$collations rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$generators rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$roles rt
                        UNION ALL
                        select rt.rdb$system_flag from rdb$auth_mapping rt
                        UNION ALL
                        select 1 from sec$users s
                        where upper(s.sec$user_name) <> 'SYSDBA'
                    ) t
                    where coalesce(t.custom_db_object_flag,0) = 0
                )
            """


            ##############################################################################
            ###  W A I T   U N T I L    R E P L I C A    B E C O M E S   A C T U A L   ###
            ##############################################################################
            watch_replica( act_db_repl, MAX_TIME_FOR_WAIT_DATA_IN_REPLICA, ddl_ready_query)

            # Must be EMPTY:
            print(capsys.readouterr().out)

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
    # Must be EMPTY:
    print(diff_meta)

#--------------------------------------------

@pytest.mark.version('>=4.0.1')
def test_1(act_db_main: Action,  act_db_repl: Action, capsys):

    out_prep, out_main, out_drop = '', '', ''

    # Obtain full path + filename for DB_MAIN and DB_REPL aliases.
    # NOTE: we must NOT use 'a.db.db_path' for ALIASED databases!
    # It will return '.' rather than full path+filename.
    # Use only con.info.name for that!
    #    
    db_info = {}
    for a in (act_db_main, act_db_repl):
        with a.db.connect(no_db_triggers = True) as con:
            if a == act_db_main and a.vars['server-arch'] == 'Classic' and os.name != 'nt':
                pytest.skip("Waiting for FIX: 'Engine is shutdown' in replication log for CS. Linux only.")
            db_info[a,  'db_full_path'] = con.info.name
            db_info[a,  'db_fw_initial'] = con.info.write_mode

    # ONLY FOR THIS test: forcedly change FW to OFF on master and ON for replica.
    #####################
    act_db_main.db.set_async_write()
    act_db_repl.db.set_sync_write()

    # Must be EMPTY:
    out_prep = capsys.readouterr().out
   
    if out_prep:
        # Some problem raised during change DB header(s)
        pass
    else:
        #N_ROWS = 30000
        N_ROWS = 20000
        FLD_WIDTH = 700

        # N_ROWS = 30'000:
        #     FW = ON ==>
        #         Added 2 segment(s) to the processing queue
        #         Segment 1 (16783004 bytes) is replicated in 1 minute(s), preserving the file due to 1 active transaction(s) ...
        #         Segment 2 (4667696 bytes) is replicated in 55 second(s), deleting the file
        #     FW = OFF ==>
    	#         Segment 1 (16783004 bytes) is replicated in 1 second(s), preserving the file due to 1 active transaction(s) ...
    	#         Segment 2 (4667696 bytes) is replicated in 374 ms, deleting the file

        current_date_with_hhmmss = datetime.today().replace(microsecond=0) # datetime.datetime(2022, 8, 26, 22, 54, 33) etc
        sql_init = f'''
            set bail on;
            recreate sequence g;
            recreate table test(id int generated by default as identity primary key, s varchar({FLD_WIDTH}), constraint test_s_unq unique(s));
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
            recreate table t_completed(id int primary key);
            commit;
        '''

        act_db_main.expected_stderr = ''
        act_db_main.isql(switches=['-q'], input = sql_init)
        out_prep = act_db_main.clean_stderr
        act_db_main.reset()

    if out_prep:
        # Some problem raised during initial data filling
        pass
    else:
        ddl_ready_query = "select 1 from rdb$relations r where r.rdb$relation_name = upper('test')"

        ##############################################################
        ###  WAIT FOR THE FIRST (BUT NOT THE ALL) DATA IN REPLICA  ###
        ##############################################################
        watch_replica( act_db_repl, MAX_TIME_FOR_WAIT_DATA_IN_REPLICA, ddl_ready_query)
        # Must be EMPTY:
        out_main = capsys.readouterr().out

    if out_main:
        # Some problem raised during check replica for appearance of table 'test' and positive value of generator 'g'.
        pass
    else:

        # Let replica to apply some part of big segment (with UUID data) for table TEST
        time.sleep(TIME_TO_LET_SEGMENTS_BE_APPLIED)

        # Here we can assume that replica is accepting segments and this work is not completed.
        # Now we change replica state to full shutdown:
        with act_db_repl.connect_server() as srv:

            # FB crashes here, replication archive folder can not be cleaned:
            # PermissionError: [WinError 32] ...: '<repl_arc_sub_dir>/<dbmain>.journal-NNN'
            srv.database.shutdown(
                                      database=act_db_repl.db.db_path
                                      ,mode=ShutdownMode.FULL
                                      ,method=ShutdownMethod.FORCED
                                      ,timeout=0
                                 )
            out_main = capsys.readouterr().out

            if not out_main:

                # We have to wait here because replication falls in pause when error occurred.
                # ("VERBOSE: Suspending for <apply_error_timeout> seconds")
                # But this delay must be LESS than <REPLICA_TIMEOUT_FOR_ERROR> to prevent from
                # SECOND suspending of replication (because bringing DB online is not instant).
                #
                #time.sleep(max(1, REPLICA_TIMEOUT_FOR_ERROR-3))

                # Without crash replication here must be resumed:
                srv.database.bring_online(
                                          database=act_db_repl.db.db_path
                                          ,mode=OnlineMode.NORMAL
                                         )
                out_main = capsys.readouterr().out

            if not out_main:
                isql_check_script = f"""
                    set list on;
                    set count on;
                    select 1 x /* check that not all data present in replica */
                    from rdb$database
                    where not exists(select * from rdb$relations where rdb$relation_name = upper('t_completed'));
                """
                isql_expected_out = f"""
                    X 1
                    Records affected: 1
                """
                ####################################################
                ###  CHECK THAT NOT ALL DATA PRESENT IN REPLICA  ###
                ####################################################
                watch_replica( act_db_repl, MAX_TIME_FOR_WAIT_DATA_IN_REPLICA, '', isql_check_script, isql_expected_out)
                # Must be EMPTY:
                out_main = capsys.readouterr().out

    if out_main:
        # Some problem raised during change state of replica DB to full shutdown or bring it online.
        pass
    else:

        # NOTE: changing DB state to full shutdown will cause following messages in the replication.log:
        #   ERROR: database <db_replica>
        #   At segment 2, offset <nnnn>
        #   VERBOSE: Suspending for <apply_error_timeout> seconds
        # (where <apply_error_timeout> = value of QA-config parameter REPLICA_TIMEOUT_FOR_ERROR)
        # Because of this, we have to wait enough time for replication resumes its work!
        
        ddl_ready_query = """
            select 1 x /* waiting for all data appears in replica */
            from rdb$relations r where r.rdb$relation_name = upper('t_completed')
        """
        ################################################
        ###  CHECK THAT ALL DATA PRESENT IN REPLICA  ###
        ################################################
        watch_replica( act_db_repl, 2 * MAX_TIME_FOR_WAIT_DATA_IN_REPLICA, ddl_ready_query)
        # Must be EMPTY:
        out_main = capsys.readouterr().out

    
    # temp dis 
    drop_db_objects(act_db_main, act_db_repl, capsys)

    # Return FW to initial values (if needed):
    for a in (act_db_main, act_db_repl):
        if db_info[a,'db_fw_initial'] == DbWriteMode.SYNC:
            a.db.set_sync_write()

    # Must be EMPTY:
    out_drop = capsys.readouterr().out

    if [ x for x in (out_prep, out_main, out_drop) if x.strip() ]:
        # We have a problem either with DDL/DML or with dropping DB objects.
        # First, we have to RECREATE both master and slave databases
        # (otherwise further execution of this test or other replication-related tests most likely will fail):
        out_reset = ''
        # temp dis  
        out_reset = reset_replication(act_db_main, act_db_repl, db_info[act_db_main,'db_full_path'], db_info[act_db_repl,'db_full_path'])

        # Next, we display out_main, out_drop and out_reset:
        #
        print('Problem(s) detected:')
        if out_prep.strip():
            print('out_prep:\n', out_prep)
        if out_main.strip():
            print('out_main:\n', out_main)
        if out_drop.strip():
            print('out_drop:\n', out_drop)
        if out_reset.strip():
            print('out_reset:\n', out_reset)

        assert '' == capsys.readouterr().out
