#coding:utf-8

"""
ID:          issue-7200
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7200
TITLE:       DROP DATABASE lead FB to hang if it is issued while DB encrypting/decrypting is in progress
DESCRIPTION:
  Test creates database that will be droppped MANUALLY (i.e. by this test itself, not by fixture).
  This database will contain table with wide indexed column and add some data to it, and its FW will be set to ON.
  Volume of data must be big enough so that the encryption thread will not complete instantly.

  Then 'ALTER DATABASE ENCRYPT...' is issued by ISQL which is launched ASYNCHRONOUSLY, and we start
  loop with query: 'select mon$crypt_state from mon$database'.
  As far as query will return column mon$crypt_state = 3 ("is encrypting") - we break from loop and try to DROP database.
  Attempt to drop database during incompleted (running) encryption must raise exception:
      lock time-out on wait transaction
      -object is in use
  Test verifies that this exception actually raises (i.e. this is EXPECTED behaviour).

  ::: NB ::: 03-mar-2023.
  We have to run second ISQL for DROP DATABASE (using 'act_tmp.isql(...)' for that).
  Attempt to use drop_database() of class Connection behaves strange on Classic: it does not return exception 'obj in use'
  and silently allows code to continue. The reason currently is unknown. To be discussed with pcisar/alex et al.

NOTES:
    [03.03.2023] pzotov
    0. On SuperServer FB 4.0.2.2772 hanged. On Classic another problem did exist: DROP DATABASE could start only after encryption
       completed (i.e. until value MON$CRYPT_STATE will not changed from 3 to 1).
    1. Settings for encryption are taken from act.files_dir/'test_config.ini' file.
    2. We have to avoid usage of act_tmp.db.drop_database() because it suppresses any occurring exception.
    3. Confirmed problem on 4.0.2.2772 SS (02-jun-2022), 5.0.0.236 SS (30-sep-2021) - test hangs.
       ::: NB :::
       FB 5.x seems to be escaped this problem much earlier than FB 4.x. Build 5.0.0.240 (01-oct-2021) altready NOT hangs.
       Checked on 5.0.0.961 SS, 4.0.3.2903 SS - all fine.

    [07.12.2023] pzotov
    Increased number of inserted rows (from 100'000 to 200'000) and indexed column width (from 700 to 800).
    Otherwise test could fail because encryption thread completes too fast (encountered under Linux).
    Loop that checks for appearance of encryption state = 3 must have delay much less than one second (changed it from 1 to 0.1).
"""

import datetime as py_dt
from pathlib import Path
import subprocess
import time
from datetime import datetime as dt

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError, tpb, Isolation, TraLockResolution, DatabaseError

FLD_LEN =   800
N_ROWS = 200000
MAX_WAIT_FOR_ENCRYPTION_START_MS = 30000

# Value in mon$crypt_state for "Database is currently encrypting"
IS_ENCRYPTING_STATE = 3

db = db_factory(page_size = 16384)
tmp_fdb = db_factory(filename = 'tmp_gh_7200.tmp.fdb')
tmp_sql = temp_file(filename = 'tmp_gh_7200.tmp.sql')
tmp_log = temp_file(filename = 'tmp_gh_7200.tmp.log')

act = python_act('db', substitutions=[('[ \t]+', ' ')])
act_tmp = python_act('tmp_fdb', substitutions=[ ('[ \t]+', ' '), ('-object .* is in use', '-object is in use'), ('(After|(-)?At) line \\d+.*', '') ])


@pytest.mark.encryption
@pytest.mark.version('>=4.0.2')
def test_1(act: Action, act_tmp: Action, tmp_sql: Path, tmp_log: Path, capsys):

    init_sql = f"""
        recreate table test(s varchar({FLD_LEN}));
        commit;
        set term ^;
        execute block as
            declare n int = {N_ROWS};
        begin
            while (n>0) do
            begin
                insert into test(s) values(lpad('', {FLD_LEN}, uuid_to_char(gen_uuid())));
                n = n - 1;
            end
        end
        ^
        -- for debug, trace must be started with log_proc = true:
        create procedure sp_debug (a_point varchar(50)) as
        begin
            -- nop --
        end
        ^
        set term ;^
        commit;
        create index test_s on test(s);
    """
    act_tmp.isql(switches=['-q'], input = init_sql, combine_output = True)
    assert act_tmp.clean_stdout == ''
    act_tmp.reset()

    #############################################
    ###   c h a n g e     F W    t o    O N   ###
    #############################################
    act_tmp.db.set_sync_write()


    # QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
    # from act.files_dir/'test_config.ini':
    enc_settings = QA_GLOBALS['encryption']

    encryption_plugin = enc_settings['encryption_plugin'] # fbSampleDbCrypt
    encryption_holder  = enc_settings['encryption_holder'] # fbSampleKeyHolder
    encryption_key = enc_settings['encryption_key'] # Red

    sttm = f'alter database encrypt with "{encryption_plugin}" key "{encryption_key}";'
    tmp_sql.write_bytes(sttm.encode('utf-8'))

    with tmp_log.open('w') as f_log:
       
        p = subprocess.Popen( [ act_tmp.vars['isql'],
                                '-q',
                                '-user', act_tmp.db.user,
                                '-password', act_tmp.db.password,
                                act_tmp.db.dsn,
                                '-i', tmp_sql
                              ], 
                              stdout = f_log, stderr = subprocess.STDOUT
                            )
    
        encryption_started = False
        with act_tmp.db.connect() as con_watcher:

            custom_tpb = tpb(isolation = Isolation.SNAPSHOT, lock_timeout = -1)
            tx_watcher = con_watcher.transaction_manager(custom_tpb)
            cur_watcher = tx_watcher.cursor()

            # 0 = non-encrypted; 1 = encrypted; 2 = is DEcrypting; 3 - is Encrypting
            ps = cur_watcher.prepare('select mon$crypt_state from mon$database')

            i = 0
            da = dt.now()
            while True:
                cur_watcher.execute(ps)
                for r in cur_watcher:
                    db_crypt_state = r[0]

                tx_watcher.commit()
                db = dt.now()
                diff_ms = (db-da).seconds*1000 + (db-da).microseconds//1000
                if db_crypt_state == IS_ENCRYPTING_STATE:
                    encryption_started = True
                    cur_watcher.call_procedure('sp_debug', ('encryption_started',))
                    break
                elif diff_ms > MAX_WAIT_FOR_ENCRYPTION_START_MS:
                    break

                time.sleep(0.1)

            ps.free()

        assert encryption_started, f'Could not find start of encryption process for {MAX_WAIT_FOR_ENCRYPTION_START_MS} ms.'

        #-----------------------------------------------------------------

        drop_db_when_running_encryption_sql = f"""
            set list on;
            select mon$crypt_state from mon$database;
            commit;
            set echo on;
            DROP DATABASE;
            set echo off;
            select lower(rdb$get_context('SYSTEM', 'DB_NAME')) as db_name from rdb$database;
        """
        tmp_sql.write_text(drop_db_when_running_encryption_sql)

        drop_db_expected_stdout = f"""
            MON$CRYPT_STATE {IS_ENCRYPTING_STATE}
            DROP DATABASE;
            Statement failed, SQLSTATE = 42000
            unsuccessful metadata update
            -object is in use
            set echo off;
            DB_NAME {str(act_tmp.db.db_path).lower()}
        """

        act_tmp.expected_stdout = drop_db_expected_stdout

        # Get current state of encryption (again, just for additional check)
        # and attempt to DROP database:
        ###############################
        act_tmp.isql(switches=['-q', '-n'], input_file = tmp_sql, combine_output=True)

        # If following assert fails then act_tmp.db.db_path was unexpectedly removed from disk:
        assert act_tmp.clean_stdout == act_tmp.clean_expected_stdout
        act_tmp.reset()

    #< with tmp_log.open('w') as f_log

    #with tmp_log.open('r') as f:
    #    print(f.read())
    #
    #act.expected_stdout = ''
    #act.stdout = capsys.readouterr().out
    #assert act.clean_stdout == act.clean_expected_stdout
