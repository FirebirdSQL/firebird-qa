#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8934
TITLE:       Local temporary tables can not be created on REPLICA database (but should).
DESCRIPTION:
    Test changes replica_mode and access mode to 'read_only'.
    Then we start read only transaction and do DDL and DML actions related to LTT.
    No error must raise.
NOTES:
    [31.03.2026] pzotov
    Confirmed problem on 6.0.0.1865-e541db2 (29.03.2026 21:06), got:
        SQLSTATE = 25006 / -attempted update during read-only transaction
    Checked on 6.0.0.1865-68b1b14.
"""
import os
import shutil
import locale
from difflib import ndiff
from pathlib import Path
import time

import pytest
from firebird.qa import *
from firebird.driver import connect, create_database, DbAccessMode, DbWriteMode, ReplicaMode, ShutdownMode, ShutdownMethod, DatabaseError


####################
ROWS_TO_INSERT = 100
####################

# QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
# from act.files_dir/'test_config.ini':
repl_settings = QA_GLOBALS['replication']

MAIN_DB_ALIAS = repl_settings['main_db_alias']
REPL_DB_ALIAS = repl_settings['repl_db_alias']
RUN_SWEEP_AT_END = int(repl_settings['run_sweep_at_end'])

db_main = db_factory( filename = '#' + MAIN_DB_ALIAS, do_not_create = True, do_not_drop = True)
db_repl = db_factory( filename = '#' + REPL_DB_ALIAS, do_not_create = True, do_not_drop = True)

substitutions = [('[\t ]+', ' ')]
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
            # ::: NB ::: 22.12.2023.
            # We have to expect that attempt to delete of GUID and (maybe) archived segments can FAIL with
            # PermissionError: [WinError 32] The process cannot ... used by another process: /path/to/{GUID}
            # Also, we have to skip exception if file (segment) was just deleted by engine
            try:
                Path(root +'/' + f).unlink(missing_ok = True)
            except PermissionError as x:
                pass

        for d in dirs:
            shutil.rmtree(os.path.join(root, d), ignore_errors = True)

    return os.listdir(p)

#--------------------------------------------

def reset_replication(act_db_main, act_db_repl, db_main_file, db_repl_file):
    out_reset = ''
    failed_shutdown_db_map = {} # K = 'db_main', 'db_repl'; V = error that occurred when we attempted to change DB state to full shutdown (if it occurred)

    with act_db_main.connect_server() as srv:

        # !! IT IS ASSUMED THAT REPLICATION FOLDERS ARE IN THE SAME DIR AS <DB_MAIN> !!
        # DO NOT use 'a.db.db_path' for ALIASED database!
        # It will return '.' rather than full path+filename.

        repl_root_path = Path(db_main_file).parent
        repl_jrn_sub_dir = Path(db_main_file).with_suffix('.journal')
        repl_arc_sub_dir = Path(db_main_file).with_suffix('.archive')

        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # xxx   s h u t d o w n    a n d    d r o p     m a s t e r    a n d    r e p l i c a   xxx
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        for f in (db_main_file, db_repl_file):
            # Method db.drop() changes LINGER to 0, issues 'delete from mon$att' with suppressing exceptions
            # and calls 'db.drop_database()' (also with suppressing exceptions).
            # We change DB state to FULL SHUTDOWN instead of call action.db.drop() because
            # this is more reliable (it kills all attachments in all known cases and does not use mon$ table)
            #
            try:
                srv.database.shutdown(database = f, mode = ShutdownMode.FULL, method = ShutdownMethod.FORCED, timeout = 0)

                # REMOVE db file from disk: we can safely assume that this can be done because DB in full shutdown state.
                ###########################
                os.unlink(f)
            except DatabaseError as e:
                failed_shutdown_db_map[ f ] = e.__str__()


        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # xxx   d e l e t e    s e g m e n t s   xxx
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # Clean folders repl_journal and repl_archive: remove all files from there.
        # NOTE: test must NOT raise unrecoverable error if some of files in these folders can not be deleted.
        # Rather, this must be displayed as diff and test must be considered as just failed.
        for p in (repl_jrn_sub_dir,repl_arc_sub_dir):
            remained_files = cleanup_folder(p)
            if remained_files:
                out_reset += '\n'.join( (f"Directory '{str(p)}' remains non-empty. Could not delete file(s):", '\n'.join(remained_files)) )

    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # xxx  r e c r e a t e     d b _ m a i n     a n d     d b _ r e p l  xxx
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    for a in (act_db_main,act_db_repl):
        d = a.db.db_path
        failed_shutdown_msg = failed_shutdown_db_map.get( str(d), '' )
        if failed_shutdown_msg:
            # we could NOT change state of this database to full shutdown --> we must NOT recreate it.
            # Accumulate error messages in OUT arg (for displaying as diff):
            #
            out_reset += '\n'.join( failed_shutdown_msg )
        else:
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
    ####################
    return out_reset

#--------------------------------------------
# NOT NEEDED IN THIS TEST: def check_repl_log ...
# NOT NEEDED IN THIS TEST: def watch_replica ...
# NOT NEEDED IN THIS TEST: def drop_db_objects ...
#--------------------------------------------

@pytest.mark.replication
@pytest.mark.version('>=6.0')
def test_1(act_db_main: Action,  act_db_repl: Action, capsys):

    out_prep, out_main  = '', ''
    # Obtain full path + filename for DB_MAIN and DB_REPL aliases.
    # NOTE: we must NOT use 'a.db.db_path' for ALIASED databases!
    # It will return '.' rather than full path+filename.
    # Use only con.info.name for that!
    #
    db_info = {}
    for a in (act_db_main, act_db_repl):
        with a.db.connect(no_db_triggers = True) as con:
            db_info[a,  'db_full_path'] = con.info.name

    srv_msg_lst = []

    if 0:
        act_db_repl.gfix( switches = ['-replica', 'read_only', act_db_repl.db.db_path], io_enc = locale.getpreferredencoding(), combine_output = True )
        srv_msg_lst.append(act_db_repl.clean_stdout)
        act_db_repl.reset()

        act_db_repl.gfix( switches = ['-mode', 'read_only', act_db_repl.db.db_path], io_enc = locale.getpreferredencoding(), combine_output = True )
        srv_msg_lst.append(act_db_repl.clean_stdout)
        act_db_repl.reset()
    else:
        with act_db_repl.connect_server() as srv:
            # forcibly set ReplicaMode to READ-ONLY because it may remain RW from some previously test that finished with runtime error:
            srv.database.set_replica_mode(database = act_db_repl.db.db_path, mode = ReplicaMode.READ_ONLY)
            srv_msg_lst.append(srv.readlines())
            #if srv_msg_lst:
            #    pass
            #else:

            # DOES NOT WORK ?!
            srv.database.set_access_mode(database = act_db_repl.db.db_path, mode = DbAccessMode.READ_ONLY)
            srv_msg_lst.append(srv.readlines())

    for p in srv_msg_lst:
        if p:
            print(p)

    # Must be EMPTY:
    out_prep = capsys.readouterr().out
    if out_prep:
        # Some problem raised during change DB header(s)
        pass
    else:
        sql_main = f'''
            set bail on;
            set list on;
            set autoterm on;
            set keep_tran on;
            commit;
            set autoddl off;
            set transaction read only;

            -- ###############################
            -- ###   c r e a t e    L T T  ###
            -- ###############################
            create local temporary table ltt_test (id int not null, uid_txt varchar(2000)) on commit preserve rows;
            commit;
            create unique descending index ltt_test_id on ltt_test(id);
            commit;
            insert into ltt_test(id, uid_txt) select row_number()over(), lpad('', 2000, uuid_to_char(gen_uuid()))
            from rdb$types rows {ROWS_TO_INSERT};
            commit;
            set count on;
            select
                d.mon$read_only as db_read_only
               ,d.mon$replica_mode as db_replica_mode
               ,t.mon$read_only as tx_read_only
               ,sign(p.mon$table_id) as ltt_table_id_sign
                 -- to check in trace that nbumber of NR equals to inserted rows:
               ,(select count(*) from ltt_test) as ltt_count_nat
                 -- to check in trace that we have INDEXED reads there on LTT:
               ,(select count(*) from ltt_test where id = 1) as ltt_count_idx
            from mon$database d
            join mon$transactions t on t.mon$transaction_id = current_transaction
            left join mon$local_temporary_tables p on p.mon$table_name = upper('ltt_test')
            ;
            set count off;
            commit;
            
            -- #############################
            -- ###   a l t e r    L T T  ###
            -- #############################
            execute block as
            begin
                execute statement ('
                    alter table ltt_test
                        drop uid_txt
                       ,add dts_tz timestamp with time zone
                       ,add addr varchar(50) character set win1250 
                        -- collate win1250_unicode ==> -COLLATION ... for CHARACTER SET ... is not defined // to be investigated
                ');
            end;
            commit;
            
            -- Check that new fields present:
            update ltt_test set
                id = -id
               ,dts_tz = '01.04.2026 12:13:14.123 Europe/Warsaw'
               ,addr = 'Kraków Główny'
            where id = (select max(id) from ltt_test)
            returning id, dts_tz, addr
            ;
            commit;

            -- ###########################
            -- ###   d r o p    L T T  ###
            -- ###########################
            drop index ltt_test_id;
            drop table ltt_test;
            commit;
            select count(*) as ltt_remains
            from mon$local_temporary_tables p
            where p.mon$table_name = upper('ltt_test');
            quit;
        '''

        act_db_repl.isql(switches = ['-q'], charset = 'utf8', input = sql_main, combine_output = True)

        act_db_repl.expected_stdout = f"""
            DB_READ_ONLY         1
            DB_REPLICA_MODE      1
            TX_READ_ONLY         1
            LTT_TABLE_ID_SIGN    1
            LTT_COUNT_NAT        {ROWS_TO_INSERT}
            LTT_COUNT_IDX        1 

            Records affected: 1

            ID                   -{ROWS_TO_INSERT}
            DTS_TZ               2026-04-01 12:13:14.1230 Europe/Warsaw
            ADDR                 Kraków Główny

            LTT_REMAINS          0
        """
        if act_db_repl.clean_stdout == act_db_repl.clean_expected_stdout:
            pass
        else:
            out_mism_lst = list( ndiff( act_db_repl.clean_expected_stdout.splitlines(), act_db_repl.clean_stdout.splitlines() ) )
            out_main = 'Mismatch(es) detected:\n' + '\n'.join( out_mism_lst )

        act_db_repl.reset()

    ########################################################################

    # in any outcome we have to return replica DB to READ_WRITE mode:
    with act_db_repl.connect_server() as srv:
        srv.database.set_access_mode(database = act_db_repl.db.db_path, mode = DbAccessMode.READ_WRITE)

    if [ x for x in (out_prep, out_main) if x.strip() ]:

        out_reset = reset_replication(act_db_main, act_db_repl, db_info[act_db_main,'db_full_path'], db_info[act_db_repl,'db_full_path'])

        print('Problem(s) detected:')
        if out_prep.strip():
            print('out_prep:')
            print(out_prep)
        if out_main.strip():
            print('out_main:')
            print(out_main)
        if out_reset.strip():
            print('out_reset:')
            print(out_reset)

        assert '' == capsys.readouterr().out
