#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/959969283621487a38fdf16c90f45ccb00b231e8
TITLE:       Avoid infinite wait due to non-optimum plan & use of read committed no record version transaction for DML by ISQL
DESCRIPTION: 
    Problem was found occasionally during re-implementing test for https://github.com/FirebirdSQL/firebird/issues/4708 aka
    CORE-4386 after shared metadata cache intro. Initial letter to FB-team: 12.04.2026 2243 (used snapshot: 6.0.0.1891-f2367d8).
    ISQL-connection that was established by ISQL and used default TIL = READ_COMMITTED_NO_RECORD_VERSION and lock_resolution = WAIT
    could not perform 'ALTER TABLE <T>' statement. ISQL hanged infinitely and should be interrupted in that case.
    This DDL could not complete even if the table <T> was for sure used only by this ISQL (see DDL actions with 'TABLE_B').

    Test can be considered as 'passed' if ISQL not hangs. Otherwise ISQL will be terminated after MAX_TIMEOUT seconds and its log
    will contain:
        e.__class__=<class 'subprocess.TimeoutExpired'>
        Command '['<path_to_isql>', '-q', '-i', '<tmp_sql_script>']' timed out after NNN seconds

NOTES:
    [15.05.2026] pzotov
        1. Original scenario that illustrated this bug (i.e. which was sent to FB-team) did use standard EMPLOYEE database.
           During attempts to reproduce the same on EMPTY database it was encountered weird thing: one need to create any *VIEW* in order
           such effect (hanging ISQL) could be observed. This view may have arbitrary DDL, even trivial query to rdb$database, see 'v_dummy'.
           Without such view, scenario will *not* reproduce bug, ISQL does not hang (and EMPLOYEE *does* has at least one view).
        2. ::: NB ::: 
           ReadConsistency = 0 must be set in databases.conf in order to reproduce bug (hanging ISQL).
           It seems that the current fix does NOT solve problem: if ReadConsistency = 0 then ISQL still hangs.
        3. One need to be sure that firebird.conf does NOT contain DatabaseAccess = None.
        4. Test uses pre-created databases.conf which has alias defined by variable REQUIRED_ALIAS.
           Database file for that alias must NOT exist in the QA_root/files/qa/ subdirectory: it will be created here.
           Content of databases.conf must be taken from $QA_ROOT/files/qa-databases.conf (one need to replace
           it before every test session).
           Discussed with pcisar, letters since 30-may-2022 13:48, subject:
           "new qa, core_4964_test.py: strange outcome when use... shutil.copy() // comparing to shutil.copy2()"
        5. Value of REQUIRED_ALIAS must be EXACTLY the same as alias specified in the pre-created databases.conf
           (for LINUX this equality is case-sensitive, even when aliases are compared!)
        Confirmed problem (ISQL hangs) on 6.0.0.1947-bbf461b
    [24.06.2026] pzotov
        Problem has been fixed in #4876bc63 ("Fixed hang when executing ALTER TABLE tableName DROP FIELD fieldName").
        Checked on 6.0.0.2028-348f7aa.
"""
import subprocess
from pathlib import Path
from firebird.driver import tpb, Isolation, TraAccessMode, DatabaseError
import time

import pytest
from firebird.qa import *

# Max time that we allow to ISQL be in 'hanging state' (terminate its process if it did not completed normally):
###############
MAX_TIMEOUT = 5
###############

# ::: ACHTUNG ::: 
# This alias in databases.conf must contain 'ReadConsistency = 0',
# i.e. ISQL which creates 3rd attachment must use *legacy* TIL = 'RC NO_RV' for DDL.
# Otherwise problem will not be reproducible, ISQL will not hang at all.
#
REQUIRED_ALIAS = 'tmp_95996928_alias'

db = db_factory(filename = '#' + REQUIRED_ALIAS)

substitutions = [ ('[ \t]+', ' '), ('After line.*', ''), ('table \\d+ is used by transaction \\d+', 'table N is used by transaction M') ] 
act = python_act('db', substitutions = substitutions)

tmp_sql = temp_file('tmp_obj_in_use.sql')
tmp_log = temp_file('tmp_obj_in_use.log')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path, capsys):

    # CONCURRENCY | NOWAIT | READ_WRITE
    tpb_snap_nowait = tpb(isolation=Isolation.SNAPSHOT, access_mode=TraAccessMode.WRITE, lock_timeout = 0)

    # CONCURRENCY | WAIT | READ_WRITE
    tpb_snap_wait = tpb(isolation=Isolation.SNAPSHOT, access_mode=TraAccessMode.WRITE, lock_timeout = -1)

    # READ_COMMITTED | NO_REC_VERSION | WAIT | READ_WRITE // isql
    #tpb_rc_norv_wait = tpb(isolation=Isolation.READ_COMMITTED_NO_RECORD_VERSION, access_mode=TraAccessMode.WRITE, lock_timeout = -1)

    # READ_COMMITTED | NO_REC_VERSION | NOWAIT | READ_WRITE
    #tpb_rc_norv_nowait = tpb(isolation=Isolation.READ_COMMITTED_NO_RECORD_VERSION, access_mode=TraAccessMode.WRITE, lock_timeout = 0)

    with act.db.connect() as cn0:

        tx0 = cn0.transaction_manager(tpb_snap_wait) # CONCURRENCY | WAIT | READ_WRITE
        tx0.begin()
       
        cu0 = tx0.cursor()

        #######################
        ###  A C H T U N G  ###
        #######################
        # This view seems to be MANDATORY to reproduce problem!
        #
        cu0.execute('recreate /* trace_me tx-0 */ view v_dummy as select 1 as id from rdb$database')
        #######################

        cu0.execute('recreate /* trace_me tx-0 */ table test_a(id int)')
        #cu0.execute("select rdb$config_value, rdb$get_context('SYSTEM', 'DB_NAME') from rdb$config where rdb$config_name = 'ReadConsistency';")
        #rc_cfg = None
        #for r in cu0:
        #    rc_cfg = 1 if r[0] else 0 # bool: True or False
        #    db_nm = r[1]

        tx0.commit()
        #print(f'ReadConsistency = {rc_cfg}')
        #print(db_nm)

        with act.db.connect() as cn1:

            tx1 = cn1.transaction_manager(tpb_snap_wait) # CONCURRENCY | WAIT | READ_WRITE
            tx1.begin()

            cu1 = tx1.cursor()
            cu1.execute('alter /* trace_me tx-1 */ table test_a add xb boolean')

            tx0 = cn0.transaction_manager(tpb_snap_nowait)
            tx0.begin()
            cu0 = tx0.cursor()
            try:
                cu0.execute('alter /* trace_me tx-0 */ table test_a add xd date') # ==> newVersion: table NNN is used by transaction MMM
                #print('tx-0: PASSED add field "xd"')
            except DatabaseError as e:
                print( e.__str__() )
                print(e.gds_codes)
            finally:
                pass

            #---------------------------------------------

            tx0.rollback()
            tx0.begin()
            try:
                cu0.execute('alter /* trace_me tx-0 try-1 */ table test_a drop id') # ==> Can't have relation with only computed fields or constraints
            except DatabaseError as e:
                print( e.__str__() )
                print(e.gds_codes)
            finally:
                pass

            #---------------------------------------------
            tx1.rollback()
            #print('done tx1.rollback()')
            #---------------------------------------------
            try:
                cu0.execute('alter /* trace_me tx-0 try-2 */ table test_a drop id')
                tx0.commit() # ==> Can't have relation with only computed fields or constraints
            except DatabaseError as e:
                print( e.__str__() )
                print(e.gds_codes)
            finally:
                pass 

            cmd_isql = [str(act.vars['isql']), '-q', '-i', str(tmp_sql)]
            test_sql = f"""
                -- {' '.join(cmd_isql)}
                set bail on;
                set list on;
                connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';
                select rdb$config_name, rdb$config_value from rdb$config where rdb$config_name = 'ReadConsistency';
                commit;
                set autoddl ON;
                recreate /* trace_me ISQL */ table test_b(id int);
                alter /* trace_me ISQL */ table test_b drop id;
            """
            tmp_sql.write_text(test_sql)

            # If the timeout expires, the child process will be killed and waited for.
            # The TimeoutExpired exception will be re-raised after the child process has terminated.
            tmp_log.unlink(missing_ok = True)
            rc = 0
            try:
                with open(tmp_log, 'w') as f:
                    ###########################
                    ###   r u n    I S Q L  ###
                    ###########################
                    # NOTE: we use 'timeout' argument here in order to prevent infinite hang of ISQL.
                    #
                    p = subprocess.run( cmd_isql, stdout = f, stderr = subprocess.STDOUT, timeout = MAX_TIMEOUT)
                    rc = p.returncode
            except Exception as e:
                print(f'{e.__class__=}')
                # DO NOT: print(f'{e.errno=}') AttributeError: 'TimeoutExpired' object has no attribute 'errno'
                # Command '[...]'  timed out after NNN seconds
                print(e.__str__())
                rc = -1 # need because timeout does not change returncode!
                
            print(f'ISQL returncode: {rc}')

            if tmp_log.is_file():
                with open(tmp_log, 'r') as f:
                    for line in f:
                        print(line)
        # < cn1
    # <  cn0

    act.expected_stdout = f"""
        unsuccessful metadata update
        -ALTER TABLE "PUBLIC"."TEST_A" failed
        -newVersion: table 128 is used by transaction 7
        (335544351, 336397287, 335544382)

        unsuccessful metadata update
        -ALTER TABLE "PUBLIC"."TEST_A" failed
        -newVersion: table 128 is used by transaction 7
        (335544351, 336397287, 335544382)

        unsuccessful metadata update
        -TABLE "PUBLIC"."TEST_A"
        -Can't have relation with only computed fields or constraints
        (335544351, 335544626, 335544858)

        ISQL returncode: 1
        RDB$CONFIG_NAME                 ReadConsistency
        RDB$CONFIG_VALUE                false

        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -TABLE "PUBLIC"."TEST_B"
        -Can't have relation with only computed fields or constraints
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
