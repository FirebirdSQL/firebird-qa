#coding:utf-8

"""
ID:          replication.failed_DDL_commands_can_be_replicated
ISSUE:       6907
TITLE:       Failed DDL commands can be replicated
DESCRIPTION:
    We create table, insert three rows in it (with null value in one of them) and, according to ticket info, run
    several DDL statements that for sure must fail, namely:
        * add new column with NOT-null requirement for its values (can not be done because nmon-empty table);
        * change DDL of existing column: add NON-null requirement to it (also can not be done because of NULL in one of rows);
        * create domain that initially allows null, then recreate table and add several rows in in (with NULL in one of them),
          and finally - try to change domain DDL by add NOT-null check. It must fail because of existing nulls in the table.

    After this we wait until replica becomes actual to master, and this delay will last no more then threshold
    that is defined by MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG variable (measured in seconds).
    During this delay, we check every second for replication log and search there line with number of last generated
    segment (which was replicated and deleting finally).
    We can assume that replication finished OK only when such line is found see ('POINT-1').
    Then we check that both databases have same data in the user table 'test'.

    Further,  we invoke ISQL with executing auxiliary script for drop all DB objects on master (with '-nod' command switch).
    After all objects will be dropped, we have to wait again until  replica becomes actual with master (see 'POINT-2').

    Finally, we extract metadata for master and replica and compare them (see 'f_meta_diff').
    The only difference in metadata must be 'CREATE DATABASE' statement with different DB names - we suppress it,
    thus metadata difference must not be issued.

    Confirmed problem on 4.0.0.126, 4.0.1.2556: message:
        "Cannot make field Y of table TEST NOT NULL because there are NULLs"
    -- is added into replication log and after this replication gets stuck.

    Checked on: 5.0.0.131 SS/CS; 4.0.1.2563 SS/CS.
FBTEST:      functional.replication.failed_DDL_commands_can_be_replicated
NOTES:
    [25.06.2021] pzotov
    1. As of 25-JUN-2021, there was a problem in FB 4.x and 5.x which can be seen on SECOND run of this test: message with text
       "ERROR: Record format with length 68 is not found for table TEST" will appear in it after inserting 1st record in master.
       The reason of that is "dirty" pages that remain in RDB$RELATION_FIELDS both on master and replica after dropping table.
       Following query show different data that appear in replica DB on 1st and 2nd run (just after table was created on master):
       =======
       set blobdisplay 6;
       select rdb$descriptor as fmt_descr
       from rdb$formats natural join rdb$relations where rdb$relation_name = 'TEST';
       =======
       This bug was explained by dimitr, see letters 25.06.2021 11:49 and 25.06.2021 16:56.
       It will be fixed later.

       The only workaround to solve this problem is to make SWEEP after all DB objects have been dropped.
       BOTH master and replica must be cleaned up by sweep!

    2. Test assumes that master and replica DB have been created beforehand.
       These two databases must NOT be neither created nor dropped in any of tests related to replication.
       They are created and dropped in the batch scenario which prepares FB instance to be checked for each ServerMode
       and make cleanup after it, i.e. when all tests will be completed.

    3. Test assumes that $FB_HOME/replication.conf has been prepared beforehand with apropriate parameters for replication.
       Particularly, parameter verbose_logging must be 'true'. Otherwise we can not get reliable outcome about whether
       segments were actually replicated or no (at least, currently - in aug-2022 - there is no way to get such info).

    [23.08.2022] pzotov
    4. Warning raises on Linux:
       ../../../usr/local/lib/python3.9/site-packages/_pytest/config/__init__.py:1126
          /usr/local/lib/python3.9/site-packages/_pytest/config/__init__.py:1126: 
          PytestAssertRewriteWarning: Module already imported so cannot be rewritten: __editable___firebird_qa_0_17_0_finder
            self._mark_plugins_for_rewrite(hook)
       The reason currently is unknown.

    Checked on 5.0.0.623, 4.0.1.2692 - both CS and SS. Both on Windows and Linux.

"""

import re
from difflib import unified_diff
from pathlib import Path
import time

import pytest
from firebird.qa import *
from firebird.driver import connect, create_database, DbWriteMode, ReplicaMode

# QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
# from act.files_dir/'test_config.ini':
repl_settings = QA_GLOBALS['replication']

MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG = int(repl_settings['max_time_for_wait_segment_in_log'])
MAIN_DB_ALIAS = repl_settings['main_db_alias']
REPL_DB_ALIAS = repl_settings['repl_db_alias']

db_main = db_factory( filename = '#' + MAIN_DB_ALIAS, do_not_create = True, do_not_drop = True)
db_repl = db_factory( filename = '#' + REPL_DB_ALIAS, do_not_create = True, do_not_drop = True)

substitutions = [('Start removing objects in:.*', 'Start removing objects'),
                 ('Finish. Total objects removed:  [1-9]\\d*', 'Finish. Total objects removed'),
                 ('.* CREATE DATABASE .*', ''),
                 ('FOUND message about replicated segment N .*', 'FOUND message about replicated segment')]
act_db_main = python_act('db_main', substitutions=substitutions)
act_db_repl = python_act('db_repl', substitutions=substitutions)

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
        print('UNEXPECTED RESULT: no message about replicating segment N {last_generated_repl_segment} for {max_allowed_time_for_wait} seconds.')

#--------------------------------------------

@pytest.mark.version('>=4.0.1')
def test_1(act_db_main: Action,  act_db_repl: Action, capsys):

    ###################
    somewhat_failed = 1
    ###################
    try:
        sql_init = f'''
            -- do NOT use in this test: -- set bail on;
            set list on;

            recreate table test(id bigint primary key, x int);
            insert into test(id, x) values(9223372036854775807, 1111);
            insert into test(id, x) values(9223372036854775806, null);
            insert into test(id, x) values(9223372036854775805, 3333);
            commit;

            -- must fail with SQLSTATE = 22006:
            alter table test add y int not null;
            commit;

            -- must fail with SQLSTATE = 22006:
            alter table test alter column x set not null;
            commit;

            create domain dm_nn int;

            recreate table test(id smallint primary key, x dm_nn);
            insert into test(id, x) values(-1, 1111);
            insert into test(id, x) values(-2, null);
            insert into test(id, x) values(-3, 3333);
            commit;

            -- must fail with SQLSTATE = 22006:
            alter domain dm_nn set not null;
            commit;
        '''
        # do NOT check STDERR of initial SQL: it must contain errors
        # because we try to run DDL statement that for sure will FAIL:

        # We *expect* errors in ISQL, so have to assign use combine_output=True and assign result to return_code:
        return_code = act_db_main.isql(switches=['-q'], input = sql_init, combine_output = True)

        act_db_main.expected_stdout = 'POINT-1 FOUND message about replicated segment N 1.'
        ##############################################################################
        ###  W A I T   U N T I L    R E P L I C A    B E C O M E S   A C T U A L   ###
        ##############################################################################
        wait_for_data_in_replica( act_db_main, MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG, 'POINT-1' )

        act_db_main.stdout = capsys.readouterr().out
        assert act_db_main.clean_stdout == act_db_main.clean_expected_stdout
        act_db_main.reset()

        #---------------------------------------------------
        
        sql_chk = '''
            set list on;
            set count on;
            select rdb$get_context('SYSTEM','REPLICA_MODE') replica_mode, t.id, t.x
            from test t
            order by t.id;
        '''
        for a in (act_db_main,act_db_repl):
            db_repl_mode = '<null>' if a == act_db_main else 'READ-ONLY'
            a.expected_stdout = f"""
                REPLICA_MODE                    {db_repl_mode}
                ID                              -3
                X                               3333
                
                REPLICA_MODE                    {db_repl_mode}
                ID                              -2
                X                               <null>

                REPLICA_MODE                    {db_repl_mode}
                ID                              -1
                X                               1111
                
                Records affected: 3
            """
            a.isql(switches=['-q'], input = sql_chk)
            assert a.clean_stdout == a.clean_expected_stdout
            a.reset()

        #-------------------------------------------------------
        
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

                
                a.expected_stdout = 'POINT-2 FOUND message about replicated segment'
                ##############################################################################
                ###  W A I T   U N T I L    R E P L I C A    B E C O M E S   A C T U A L   ###
                ##############################################################################
                wait_for_data_in_replica( a, MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG, 'POINT-2' )

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
    finally:
        pass

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
                        con.execute_immediate('alter database enable publication')
                        con.execute_immediate('alter database include all to publication')
                        con.commit()

    assert somewhat_failed == 0
