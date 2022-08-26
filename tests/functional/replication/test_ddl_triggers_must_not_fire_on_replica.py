#coding:utf-8
"""
ID:          replication.ddl_triggers_must_not_fire_on_replica
TITLE:       DDL-triggers must fire only on master DB
DESCRIPTION:
    Test creates all kinds of DDL triggers in the master DB.
    Each of them registers apropriate event in the table with name 'log_ddl_triggers_activity'.
    After this we create all kinds of DB objects (tables, procedure, function, etc) in master DB to fire these triggers.

    Then we wait until replica becomes actual to master, and this delay will last no more then threshold
    that is defined by MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG variable (measured in seconds).
    During this delay, we check every second for replication log and search there line with number of last generated
    segment (which was replicated and deleting finally).
    We can assume that replication finished OK only when such line is found see ('POINT-1').

    After this, we do following:
    1) compare metadata of master and replica DB, they must be equal (except file names);
    2) obtain data from 'log_ddl_triggers_activity' table:
      2.1) on master it must have record about every DDL-trigger that fired;
      2.2) on replica this table must be EMPTY (bacause DDL triggers must not fire on replica).

    Then we invoke ISQL with executing auxiliary script for drop all DB objects on master (with '-nod' command switch).
    After all objects will be dropped, we have to wait again until replica becomes actual with master (see 'POINT-2').

    Finally, we extract metadata for master and replica after this cleanup and compare them.

FBTEST:      tests.functional.replication.ddl_triggers_must_not_fire_on_replica
NOTES:
    [25.08.2022] pzotov
    1. In case of any errors (somewhat_failed <> 0) test will re-create db_main and db_repl, and then perform all needed
       actions to resume replication (set 'replica' flag on db_repl, enabling publishing in db_main, remove all files
       from subdirectories <repl_journal> and <repl_archive> which must present in the same folder as <db_main>).
    2. Warning raises on Windows and Linux:
       ../../../usr/local/lib/python3.9/site-packages/_pytest/config/__init__.py:1126
          /usr/local/lib/python3.9/site-packages/_pytest/config/__init__.py:1126: 
          PytestAssertRewriteWarning: Module already imported so cannot be rewritten: __editable___firebird_qa_0_17_0_finder
            self._mark_plugins_for_rewrite(hook)
       The reason currently is unknown.

    Checked on 5.0.0.623, 4.0.1.2692 - both CS and SS. Both on Windows and Linux.
"""

import os
import shutil
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
                 ('[\t ]+', ' '),
                 ('FOUND message about replicated segment N .*', 'FOUND message about replicated segment')]

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
        print('UNEXPECTED RESULT: no message about replicating segment N {last_generated_repl_segment} for {max_allowed_time_for_wait} seconds.')

#--------------------------------------------

@pytest.mark.version('>=4.0.1')
def test_1(act_db_main: Action,  act_db_repl: Action, capsys):

    #assert '' == capsys.readouterr().out

    ###################
    somewhat_failed = 1
    ###################
    try:

        sql_init = '''    
            set bail on;
            set list on;

            select mon$database_name from mon$database;

            recreate table log_ddl_triggers_activity (
                id int generated by default as identity constraint pk_log_ddl_triggers_activity primary key
                ,ddl_trigger_name varchar(64)
                ,event_type varchar(25) not null
                ,object_type varchar(25) not null
                ,ddl_event varchar(25) not null
                ,object_name varchar(64) not null
            );


            set term ^;
            execute block as
                declare v_lf char(1) = x'0A';
            begin
                rdb$set_context('USER_SESSION', 'SKIP_DDL_TRIGGER', '1');

                for
                    with
                    a as (
                        select 'ANY DDL STATEMENT' x from rdb$database union all
                        select 'CREATE TABLE' from rdb$database union all
                        select 'ALTER TABLE' from rdb$database union all
                        select 'DROP TABLE' from rdb$database union all
                        select 'CREATE PROCEDURE' from rdb$database union all
                        select 'ALTER PROCEDURE' from rdb$database union all
                        select 'DROP PROCEDURE' from rdb$database union all
                        select 'CREATE FUNCTION' from rdb$database union all
                        select 'ALTER FUNCTION' from rdb$database union all
                        select 'DROP FUNCTION' from rdb$database union all
                        select 'CREATE TRIGGER' from rdb$database union all
                        select 'ALTER TRIGGER' from rdb$database union all
                        select 'DROP TRIGGER' from rdb$database union all
                        select 'CREATE EXCEPTION' from rdb$database union all
                        select 'ALTER EXCEPTION' from rdb$database union all
                        select 'DROP EXCEPTION' from rdb$database union all
                        select 'CREATE VIEW' from rdb$database union all
                        select 'ALTER VIEW' from rdb$database union all
                        select 'DROP VIEW' from rdb$database union all
                        select 'CREATE DOMAIN' from rdb$database union all
                        select 'ALTER DOMAIN' from rdb$database union all
                        select 'DROP DOMAIN' from rdb$database union all
                        select 'CREATE ROLE' from rdb$database union all
                        select 'ALTER ROLE' from rdb$database union all
                        select 'DROP ROLE' from rdb$database union all
                        select 'CREATE SEQUENCE' from rdb$database union all
                        select 'ALTER SEQUENCE' from rdb$database union all
                        select 'DROP SEQUENCE' from rdb$database union all
                        select 'CREATE USER' from rdb$database union all
                        select 'ALTER USER' from rdb$database union all
                        select 'DROP USER' from rdb$database union all
                        select 'CREATE INDEX' from rdb$database union all
                        select 'ALTER INDEX' from rdb$database union all
                        select 'DROP INDEX' from rdb$database union all
                        select 'CREATE COLLATION' from rdb$database union all
                        select 'DROP COLLATION' from rdb$database union all
                        select 'ALTER CHARACTER SET' from rdb$database union all
                        select 'CREATE PACKAGE' from rdb$database union all
                        select 'ALTER PACKAGE' from rdb$database union all
                        select 'DROP PACKAGE' from rdb$database union all
                        select 'CREATE PACKAGE BODY' from rdb$database union all
                        select 'DROP PACKAGE BODY' from rdb$database
                    )
                    ,e as (
                        select 'before' w from rdb$database union all select 'after' from rdb$database
                    )
                    ,t as (
                        select upper(trim(replace(trim(a.x),' ','_')) || iif(e.w='before', '_before', '_after')) as trg_name, a.x, e.w
                        from e, a
                    )

                    select
                           'create or alter trigger trg_' || t.trg_name
                        || ' active ' || t.w || ' ' || trim(t.x) || ' as '
                        || :v_lf
                        || 'begin'
                        || :v_lf
                        || q'{    if (rdb$get_context('USER_SESSION', 'SKIP_DDL_TRIGGER') is null) then}'
                        || :v_lf
                        || '        insert into log_ddl_triggers_activity(ddl_trigger_name, event_type, object_type, ddl_event, object_name) values('
                        || :v_lf
                        || q'{'}' || trim(t.trg_name) || q'{'}'
                        || :v_lf
                        || q'{, rdb$get_context('DDL_TRIGGER', 'EVENT_TYPE')}'
                        || :v_lf
                        || q'{, rdb$get_context('DDL_TRIGGER', 'OBJECT_TYPE')}'
                        || :v_lf
                        || q'{, rdb$get_context('DDL_TRIGGER', 'DDL_EVENT')}'
                        || :v_lf
                        || q'{, rdb$get_context('DDL_TRIGGER', 'OBJECT_NAME')}'
                        || :v_lf
                        || ');'
                        || :v_lf
                        || ' end'
                        as sttm
                    from t
                    as cursor c
                 do begin
                     execute statement(c.sttm) with autonomous transaction;
                 end

                rdb$set_context('USER_SESSION', 'SKIP_DDL_TRIGGER', null);
            end
            ^
            set term ;^
            commit;

            /*
            select rt.rdb$trigger_name,rt.rdb$relation_name,rt.rdb$trigger_type,rt.rdb$trigger_source
            from rdb$triggers rt
            where
                rt.rdb$system_flag is distinct from 1
                and rt.rdb$trigger_inactive is distinct from 1;

            select * from log_ddl_triggers_activity;
            */

            -- set count on;
            -- set echo on;

            set term ^;

            create table test(id int not null, name varchar(10))
            ^
            alter table test add constraint test_pk primary key(id)
            ^
            ----------
            create procedure sp_test as begin end
            ^
            alter procedure sp_test as declare x int; begin x=1; end
            ^
            ----------
            create function fn_test(a_id int) returns bigint as
            begin
                return a_id * a_id;
            end
            ^
            alter function fn_test(a_id int) returns int128 as
            begin
                return a_id * a_id * a_id;
            end
            ^
            ----------
            create trigger trg_connect_test on connect as
            begin
            end
            ^
            alter trigger trg_connect_test as
                declare x int;
            begin
                x = 1;
            end
            ^
            ----------
            create exception exc_test 'Invalud value: @1'
            ^
            alter exception exc_test 'Bad values: @1 and @2'
            ^
            ----------
            create view v_test as select 1 x from rdb$database
            ^
            alter view v_test as select 1 x, 2 y from rdb$database
            ^
            ----------
            create domain dm_test int
            ^
            alter domain dm_test set not null
            ^
            ----------
            create role r_test
            ^
            alter role r_test set system privileges to use_gstat_utility, ignore_db_triggers
            ^
            ----------
            create sequence g_test
            ^
            alter sequence g_test restart with 123
            ^
            ----------
            /*
            create or alter user u_test password '123' using plugin Srp
            ^
            alter user u_test password '456'
            ^
            */
            ----------
            create index test_name on test(name)
            ^
            alter index test_name inactive
            ^
            ----------
            create collation name_coll for utf8 from unicode case insensitive
            ^
            ----------
            alter character set iso8859_1 set default collation pt_br
            ^
            ----------
            create or alter package pg_test as
            begin
               function pg_fn1 returns int;
            end
            ^
            alter package pg_test as
            begin
               function pg_fn1(a_x int) returns int128;
            end
            ^

            create package body pg_test as
            begin
               function pg_fn1(a_x int) returns int128 as
               begin
                   return a_x * a_x * a_x;
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

        act_db_main.expected_stdout = 'POINT-1 FOUND message about replicated segment'
        ##############################################################################
        ###  W A I T   U N T I L    R E P L I C A    B E C O M E S   A C T U A L   ###
        ##############################################################################
        wait_for_data_in_replica( act_db_main, MAX_TIME_FOR_WAIT_SEGMENT_IN_LOG, 'POINT-1' )

        act_db_main.stdout = capsys.readouterr().out
        assert act_db_main.clean_stdout == act_db_main.clean_expected_stdout
        act_db_main.reset()

        #---------------------------------------------------
        
        for a in (act_db_main,act_db_repl):
            db_name = a.db.db_path.upper()
            sql_chk = f'''
                set list on;
                set count on;
                select
                    '{db_name}' as db_name
                    ,a.id
                    ,a.ddl_trigger_name
                    ,a.event_type
                    ,a.object_type
                    ,a.ddl_event
                    ,a.object_name
                from log_ddl_triggers_activity a
                order by a.id;
            '''

            if a == act_db_main:
                a.expected_stdout = f"""
                    DB_NAME {db_name}
                    ID 1
                    DDL_TRIGGER_NAME CREATE_TABLE_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE TABLE
                    DDL_EVENT CREATE TABLE
                    OBJECT_NAME TEST
                    DB_NAME {db_name}
                    ID 2
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE TABLE
                    DDL_EVENT CREATE TABLE
                    OBJECT_NAME TEST
                    DB_NAME {db_name}
                    ID 3
                    DDL_TRIGGER_NAME CREATE_TABLE_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE TABLE
                    DDL_EVENT CREATE TABLE
                    OBJECT_NAME TEST
                    DB_NAME {db_name}
                    ID 4
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE TABLE
                    DDL_EVENT CREATE TABLE
                    OBJECT_NAME TEST
                    DB_NAME {db_name}
                    ID 5
                    DDL_TRIGGER_NAME ALTER_TABLE_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE TABLE
                    DDL_EVENT ALTER TABLE
                    OBJECT_NAME TEST
                    DB_NAME {db_name}
                    ID 6
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE TABLE
                    DDL_EVENT ALTER TABLE
                    OBJECT_NAME TEST
                    DB_NAME {db_name}
                    ID 7
                    DDL_TRIGGER_NAME ALTER_TABLE_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE TABLE
                    DDL_EVENT ALTER TABLE
                    OBJECT_NAME TEST
                    DB_NAME {db_name}
                    ID 8
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE TABLE
                    DDL_EVENT ALTER TABLE
                    OBJECT_NAME TEST
                    DB_NAME {db_name}
                    ID 9
                    DDL_TRIGGER_NAME CREATE_PROCEDURE_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PROCEDURE
                    DDL_EVENT CREATE PROCEDURE
                    OBJECT_NAME SP_TEST
                    DB_NAME {db_name}
                    ID 10
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PROCEDURE
                    DDL_EVENT CREATE PROCEDURE
                    OBJECT_NAME SP_TEST
                    DB_NAME {db_name}
                    ID 11
                    DDL_TRIGGER_NAME CREATE_PROCEDURE_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PROCEDURE
                    DDL_EVENT CREATE PROCEDURE
                    OBJECT_NAME SP_TEST
                    DB_NAME {db_name}
                    ID 12
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PROCEDURE
                    DDL_EVENT CREATE PROCEDURE
                    OBJECT_NAME SP_TEST
                    DB_NAME {db_name}
                    ID 13
                    DDL_TRIGGER_NAME ALTER_PROCEDURE_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE PROCEDURE
                    DDL_EVENT ALTER PROCEDURE
                    OBJECT_NAME SP_TEST
                    DB_NAME {db_name}
                    ID 14
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE PROCEDURE
                    DDL_EVENT ALTER PROCEDURE
                    OBJECT_NAME SP_TEST
                    DB_NAME {db_name}
                    ID 15
                    DDL_TRIGGER_NAME ALTER_PROCEDURE_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE PROCEDURE
                    DDL_EVENT ALTER PROCEDURE
                    OBJECT_NAME SP_TEST
                    DB_NAME {db_name}
                    ID 16
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE PROCEDURE
                    DDL_EVENT ALTER PROCEDURE
                    OBJECT_NAME SP_TEST
                    DB_NAME {db_name}
                    ID 17
                    DDL_TRIGGER_NAME CREATE_FUNCTION_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE FUNCTION
                    DDL_EVENT CREATE FUNCTION
                    OBJECT_NAME FN_TEST
                    DB_NAME {db_name}
                    ID 18
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE FUNCTION
                    DDL_EVENT CREATE FUNCTION
                    OBJECT_NAME FN_TEST
                    DB_NAME {db_name}
                    ID 19
                    DDL_TRIGGER_NAME CREATE_FUNCTION_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE FUNCTION
                    DDL_EVENT CREATE FUNCTION
                    OBJECT_NAME FN_TEST
                    DB_NAME {db_name}
                    ID 20
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE FUNCTION
                    DDL_EVENT CREATE FUNCTION
                    OBJECT_NAME FN_TEST
                    DB_NAME {db_name}
                    ID 21
                    DDL_TRIGGER_NAME ALTER_FUNCTION_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE FUNCTION
                    DDL_EVENT ALTER FUNCTION
                    OBJECT_NAME FN_TEST
                    DB_NAME {db_name}
                    ID 22
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE FUNCTION
                    DDL_EVENT ALTER FUNCTION
                    OBJECT_NAME FN_TEST
                    DB_NAME {db_name}
                    ID 23
                    DDL_TRIGGER_NAME ALTER_FUNCTION_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE FUNCTION
                    DDL_EVENT ALTER FUNCTION
                    OBJECT_NAME FN_TEST
                    DB_NAME {db_name}
                    ID 24
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE FUNCTION
                    DDL_EVENT ALTER FUNCTION
                    OBJECT_NAME FN_TEST
                    DB_NAME {db_name}
                    ID 25
                    DDL_TRIGGER_NAME CREATE_TRIGGER_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE TRIGGER
                    DDL_EVENT CREATE TRIGGER
                    OBJECT_NAME TRG_CONNECT_TEST
                    DB_NAME {db_name}
                    ID 26
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE TRIGGER
                    DDL_EVENT CREATE TRIGGER
                    OBJECT_NAME TRG_CONNECT_TEST
                    DB_NAME {db_name}
                    ID 27
                    DDL_TRIGGER_NAME CREATE_TRIGGER_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE TRIGGER
                    DDL_EVENT CREATE TRIGGER
                    OBJECT_NAME TRG_CONNECT_TEST
                    DB_NAME {db_name}
                    ID 28
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE TRIGGER
                    DDL_EVENT CREATE TRIGGER
                    OBJECT_NAME TRG_CONNECT_TEST
                    DB_NAME {db_name}
                    ID 29
                    DDL_TRIGGER_NAME ALTER_TRIGGER_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE TRIGGER
                    DDL_EVENT ALTER TRIGGER
                    OBJECT_NAME TRG_CONNECT_TEST
                    DB_NAME {db_name}
                    ID 30
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE TRIGGER
                    DDL_EVENT ALTER TRIGGER
                    OBJECT_NAME TRG_CONNECT_TEST
                    DB_NAME {db_name}
                    ID 31
                    DDL_TRIGGER_NAME ALTER_TRIGGER_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE TRIGGER
                    DDL_EVENT ALTER TRIGGER
                    OBJECT_NAME TRG_CONNECT_TEST
                    DB_NAME {db_name}
                    ID 32
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE TRIGGER
                    DDL_EVENT ALTER TRIGGER
                    OBJECT_NAME TRG_CONNECT_TEST
                    DB_NAME {db_name}
                    ID 33
                    DDL_TRIGGER_NAME CREATE_EXCEPTION_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE EXCEPTION
                    DDL_EVENT CREATE EXCEPTION
                    OBJECT_NAME EXC_TEST
                    DB_NAME {db_name}
                    ID 34
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE EXCEPTION
                    DDL_EVENT CREATE EXCEPTION
                    OBJECT_NAME EXC_TEST
                    DB_NAME {db_name}
                    ID 35
                    DDL_TRIGGER_NAME CREATE_EXCEPTION_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE EXCEPTION
                    DDL_EVENT CREATE EXCEPTION
                    OBJECT_NAME EXC_TEST
                    DB_NAME {db_name}
                    ID 36
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE EXCEPTION
                    DDL_EVENT CREATE EXCEPTION
                    OBJECT_NAME EXC_TEST
                    DB_NAME {db_name}
                    ID 37
                    DDL_TRIGGER_NAME ALTER_EXCEPTION_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE EXCEPTION
                    DDL_EVENT ALTER EXCEPTION
                    OBJECT_NAME EXC_TEST
                    DB_NAME {db_name}
                    ID 38
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE EXCEPTION
                    DDL_EVENT ALTER EXCEPTION
                    OBJECT_NAME EXC_TEST
                    DB_NAME {db_name}
                    ID 39
                    DDL_TRIGGER_NAME ALTER_EXCEPTION_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE EXCEPTION
                    DDL_EVENT ALTER EXCEPTION
                    OBJECT_NAME EXC_TEST
                    DB_NAME {db_name}
                    ID 40
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE EXCEPTION
                    DDL_EVENT ALTER EXCEPTION
                    OBJECT_NAME EXC_TEST
                    DB_NAME {db_name}
                    ID 41
                    DDL_TRIGGER_NAME CREATE_VIEW_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE VIEW
                    DDL_EVENT CREATE VIEW
                    OBJECT_NAME V_TEST
                    DB_NAME {db_name}
                    ID 42
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE VIEW
                    DDL_EVENT CREATE VIEW
                    OBJECT_NAME V_TEST
                    DB_NAME {db_name}
                    ID 43
                    DDL_TRIGGER_NAME CREATE_VIEW_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE VIEW
                    DDL_EVENT CREATE VIEW
                    OBJECT_NAME V_TEST
                    DB_NAME {db_name}
                    ID 44
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE VIEW
                    DDL_EVENT CREATE VIEW
                    OBJECT_NAME V_TEST
                    DB_NAME {db_name}
                    ID 45
                    DDL_TRIGGER_NAME ALTER_VIEW_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE VIEW
                    DDL_EVENT ALTER VIEW
                    OBJECT_NAME V_TEST
                    DB_NAME {db_name}
                    ID 46
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE VIEW
                    DDL_EVENT ALTER VIEW
                    OBJECT_NAME V_TEST
                    DB_NAME {db_name}
                    ID 47
                    DDL_TRIGGER_NAME ALTER_VIEW_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE VIEW
                    DDL_EVENT ALTER VIEW
                    OBJECT_NAME V_TEST
                    DB_NAME {db_name}
                    ID 48
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE VIEW
                    DDL_EVENT ALTER VIEW
                    OBJECT_NAME V_TEST
                    DB_NAME {db_name}
                    ID 49
                    DDL_TRIGGER_NAME CREATE_DOMAIN_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE DOMAIN
                    DDL_EVENT CREATE DOMAIN
                    OBJECT_NAME DM_TEST
                    DB_NAME {db_name}
                    ID 50
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE DOMAIN
                    DDL_EVENT CREATE DOMAIN
                    OBJECT_NAME DM_TEST
                    DB_NAME {db_name}
                    ID 51
                    DDL_TRIGGER_NAME CREATE_DOMAIN_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE DOMAIN
                    DDL_EVENT CREATE DOMAIN
                    OBJECT_NAME DM_TEST
                    DB_NAME {db_name}
                    ID 52
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE DOMAIN
                    DDL_EVENT CREATE DOMAIN
                    OBJECT_NAME DM_TEST
                    DB_NAME {db_name}
                    ID 53
                    DDL_TRIGGER_NAME ALTER_DOMAIN_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE DOMAIN
                    DDL_EVENT ALTER DOMAIN
                    OBJECT_NAME DM_TEST
                    DB_NAME {db_name}
                    ID 54
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE DOMAIN
                    DDL_EVENT ALTER DOMAIN
                    OBJECT_NAME DM_TEST
                    DB_NAME {db_name}
                    ID 55
                    DDL_TRIGGER_NAME ALTER_DOMAIN_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE DOMAIN
                    DDL_EVENT ALTER DOMAIN
                    OBJECT_NAME DM_TEST
                    DB_NAME {db_name}
                    ID 56
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE DOMAIN
                    DDL_EVENT ALTER DOMAIN
                    OBJECT_NAME DM_TEST
                    DB_NAME {db_name}
                    ID 57
                    DDL_TRIGGER_NAME CREATE_ROLE_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE ROLE
                    DDL_EVENT CREATE ROLE
                    OBJECT_NAME R_TEST
                    DB_NAME {db_name}
                    ID 58
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE ROLE
                    DDL_EVENT CREATE ROLE
                    OBJECT_NAME R_TEST
                    DB_NAME {db_name}
                    ID 59
                    DDL_TRIGGER_NAME CREATE_ROLE_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE ROLE
                    DDL_EVENT CREATE ROLE
                    OBJECT_NAME R_TEST
                    DB_NAME {db_name}
                    ID 60
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE ROLE
                    DDL_EVENT CREATE ROLE
                    OBJECT_NAME R_TEST
                    DB_NAME {db_name}
                    ID 61
                    DDL_TRIGGER_NAME ALTER_ROLE_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE ROLE
                    DDL_EVENT ALTER ROLE
                    OBJECT_NAME R_TEST
                    DB_NAME {db_name}
                    ID 62
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE ROLE
                    DDL_EVENT ALTER ROLE
                    OBJECT_NAME R_TEST
                    DB_NAME {db_name}
                    ID 63
                    DDL_TRIGGER_NAME ALTER_ROLE_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE ROLE
                    DDL_EVENT ALTER ROLE
                    OBJECT_NAME R_TEST
                    DB_NAME {db_name}
                    ID 64
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE ROLE
                    DDL_EVENT ALTER ROLE
                    OBJECT_NAME R_TEST
                    DB_NAME {db_name}
                    ID 65
                    DDL_TRIGGER_NAME CREATE_SEQUENCE_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE SEQUENCE
                    DDL_EVENT CREATE SEQUENCE
                    OBJECT_NAME G_TEST
                    DB_NAME {db_name}
                    ID 66
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE SEQUENCE
                    DDL_EVENT CREATE SEQUENCE
                    OBJECT_NAME G_TEST
                    DB_NAME {db_name}
                    ID 67
                    DDL_TRIGGER_NAME CREATE_SEQUENCE_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE SEQUENCE
                    DDL_EVENT CREATE SEQUENCE
                    OBJECT_NAME G_TEST
                    DB_NAME {db_name}
                    ID 68
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE SEQUENCE
                    DDL_EVENT CREATE SEQUENCE
                    OBJECT_NAME G_TEST
                    DB_NAME {db_name}
                    ID 69
                    DDL_TRIGGER_NAME ALTER_SEQUENCE_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE SEQUENCE
                    DDL_EVENT ALTER SEQUENCE
                    OBJECT_NAME G_TEST
                    DB_NAME {db_name}
                    ID 70
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE SEQUENCE
                    DDL_EVENT ALTER SEQUENCE
                    OBJECT_NAME G_TEST
                    DB_NAME {db_name}
                    ID 71
                    DDL_TRIGGER_NAME ALTER_SEQUENCE_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE SEQUENCE
                    DDL_EVENT ALTER SEQUENCE
                    OBJECT_NAME G_TEST
                    DB_NAME {db_name}
                    ID 72
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE SEQUENCE
                    DDL_EVENT ALTER SEQUENCE
                    OBJECT_NAME G_TEST
                    DB_NAME {db_name}
                    ID 73
                    DDL_TRIGGER_NAME CREATE_INDEX_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE INDEX
                    DDL_EVENT CREATE INDEX
                    OBJECT_NAME TEST_NAME
                    DB_NAME {db_name}
                    ID 74
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE INDEX
                    DDL_EVENT CREATE INDEX
                    OBJECT_NAME TEST_NAME
                    DB_NAME {db_name}
                    ID 75
                    DDL_TRIGGER_NAME CREATE_INDEX_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE INDEX
                    DDL_EVENT CREATE INDEX
                    OBJECT_NAME TEST_NAME
                    DB_NAME {db_name}
                    ID 76
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE INDEX
                    DDL_EVENT CREATE INDEX
                    OBJECT_NAME TEST_NAME
                    DB_NAME {db_name}
                    ID 77
                    DDL_TRIGGER_NAME ALTER_INDEX_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE INDEX
                    DDL_EVENT ALTER INDEX
                    OBJECT_NAME TEST_NAME
                    DB_NAME {db_name}
                    ID 78
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE INDEX
                    DDL_EVENT ALTER INDEX
                    OBJECT_NAME TEST_NAME
                    DB_NAME {db_name}
                    ID 79
                    DDL_TRIGGER_NAME ALTER_INDEX_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE INDEX
                    DDL_EVENT ALTER INDEX
                    OBJECT_NAME TEST_NAME
                    DB_NAME {db_name}
                    ID 80
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE INDEX
                    DDL_EVENT ALTER INDEX
                    OBJECT_NAME TEST_NAME
                    DB_NAME {db_name}
                    ID 81
                    DDL_TRIGGER_NAME CREATE_COLLATION_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE COLLATION
                    DDL_EVENT CREATE COLLATION
                    OBJECT_NAME NAME_COLL
                    DB_NAME {db_name}
                    ID 82
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE COLLATION
                    DDL_EVENT CREATE COLLATION
                    OBJECT_NAME NAME_COLL
                    DB_NAME {db_name}
                    ID 83
                    DDL_TRIGGER_NAME CREATE_COLLATION_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE COLLATION
                    DDL_EVENT CREATE COLLATION
                    OBJECT_NAME NAME_COLL
                    DB_NAME {db_name}
                    ID 84
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE COLLATION
                    DDL_EVENT CREATE COLLATION
                    OBJECT_NAME NAME_COLL
                    DB_NAME {db_name}
                    ID 85
                    DDL_TRIGGER_NAME ALTER_CHARACTER_SET_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE CHARACTER SET
                    DDL_EVENT ALTER CHARACTER SET
                    OBJECT_NAME ISO8859_1
                    DB_NAME {db_name}
                    ID 86
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE CHARACTER SET
                    DDL_EVENT ALTER CHARACTER SET
                    OBJECT_NAME ISO8859_1
                    DB_NAME {db_name}
                    ID 87
                    DDL_TRIGGER_NAME ALTER_CHARACTER_SET_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE CHARACTER SET
                    DDL_EVENT ALTER CHARACTER SET
                    OBJECT_NAME ISO8859_1
                    DB_NAME {db_name}
                    ID 88
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE CHARACTER SET
                    DDL_EVENT ALTER CHARACTER SET
                    OBJECT_NAME ISO8859_1
                    DB_NAME {db_name}
                    ID 89
                    DDL_TRIGGER_NAME CREATE_PACKAGE_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PACKAGE
                    DDL_EVENT CREATE PACKAGE
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 90
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PACKAGE
                    DDL_EVENT CREATE PACKAGE
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 91
                    DDL_TRIGGER_NAME CREATE_PACKAGE_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PACKAGE
                    DDL_EVENT CREATE PACKAGE
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 92
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PACKAGE
                    DDL_EVENT CREATE PACKAGE
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 93
                    DDL_TRIGGER_NAME ALTER_PACKAGE_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE PACKAGE
                    DDL_EVENT ALTER PACKAGE
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 94
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE ALTER
                    OBJECT_TYPE PACKAGE
                    DDL_EVENT ALTER PACKAGE
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 95
                    DDL_TRIGGER_NAME ALTER_PACKAGE_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE PACKAGE
                    DDL_EVENT ALTER PACKAGE
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 96
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE ALTER
                    OBJECT_TYPE PACKAGE
                    DDL_EVENT ALTER PACKAGE
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 97
                    DDL_TRIGGER_NAME CREATE_PACKAGE_BODY_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PACKAGE BODY
                    DDL_EVENT CREATE PACKAGE BODY
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 98
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_BEFORE
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PACKAGE BODY
                    DDL_EVENT CREATE PACKAGE BODY
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 99
                    DDL_TRIGGER_NAME CREATE_PACKAGE_BODY_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PACKAGE BODY
                    DDL_EVENT CREATE PACKAGE BODY
                    OBJECT_NAME PG_TEST
                    DB_NAME {db_name}
                    ID 100
                    DDL_TRIGGER_NAME ANY_DDL_STATEMENT_AFTER
                    EVENT_TYPE CREATE
                    OBJECT_TYPE PACKAGE BODY
                    DDL_EVENT CREATE PACKAGE BODY
                    OBJECT_NAME PG_TEST
                    Records affected: 100
                """
            else: # a == act_db_repl --> NO recors about fired DDL triggers must be found!
                a.expected_stdout = f"""
                    Records affected: 0
                """

            a.isql(switches=['-q', '-nod'], input = sql_chk)
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
                        # !! IT IS ASSUMED THAT REPLICATION FOLDERS ARE IN THE SAME DIR AS <DB_MAIN> !!
                        # DO NOT use 'a.db.db_path' for ALIASED database!
                        # Its '.parent' property will be '.' rather than full path.
                        # Use only con.info.name for that:
                        repl_root_path = Path(con.info.name).parent
                        repl_jrn_sub_dir = repl_settings['journal_sub_dir']
                        repl_arc_sub_dir = repl_settings['archive_sub_dir']

                        # Clean folders repl_journal and repl_archive (remove all files from there):
                        for p in (repl_jrn_sub_dir,repl_arc_sub_dir):
                            assert cleanup_folder(repl_root_path / p) == 0, f"Directory {str(p)} remains non-empty."

                        con.execute_immediate('alter database enable publication')
                        con.execute_immediate('alter database include all to publication')
                        con.commit()

    assert somewhat_failed == 0
