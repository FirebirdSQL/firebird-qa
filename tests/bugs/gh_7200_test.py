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
  As far as query will return columd value = 3 ("is encrypting") - we break from loop and try to DROP database.
  Attempt to drop database which has incompleted encryption must raise exception:
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
"""

import datetime as py_dt
from pathlib import Path
import subprocess
import time

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError, tpb, Isolation, TraLockResolution, DatabaseError

FLD_LEN =   500
N_ROWS = 100000
ENCRYPTION_START_MAX_WAIT = 30

# Value in mon$crypt_state for "Database is currently encrypting"
IS_ENCRYPTING_STATE = 3

db = db_factory()
tmp_fdb = db_factory(filename = 'tmp_gh_7200.tmp.fdb')
tmp_sql = temp_file(filename = 'tmp_gh_7200.tmp.sql')
tmp_log = temp_file(filename = 'tmp_gh_7200.tmp.log')

act = python_act('db', substitutions=[('[ \t]+', ' ')])
act_tmp = python_act('tmp_fdb', substitutions=[('-object .* is in use', '-object is in use')])

expected_stdout = """
"""

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
        create procedure sp_tmp (a_point varchar(50)) as
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

    act_tmp.db.set_sync_write() # here we want DB be encrypted for some *valuable* time

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
            while True:
                cur_watcher.execute(ps)
                for r in cur_watcher:
                    db_crypt_state = r[0]

                tx_watcher.commit()

                if db_crypt_state == IS_ENCRYPTING_STATE:
                    encryption_started = True
                    cur_watcher.call_procedure('sp_tmp', ('encryption_started',))
                    break
                elif i > ENCRYPTION_START_MAX_WAIT:
                    break

                time.sleep(1)

            ps.free()

        assert encryption_started, f'Could not find start of encryption process for {ENCRYPTION_START_MAX_WAIT} seconds.'

        drop_db_expected_stdout = f"""
            MON$CRYPT_STATE                 {IS_ENCRYPTING_STATE}
            Statement failed, SQLSTATE = 42000
            unsuccessful metadata update
            -object is in use        
        """

        act_tmp.expected_stdout = drop_db_expected_stdout

        # Get current state of encryption (again, just for additional check)
        # and attempt to DROP database:
        ###############################
        act_tmp.isql(switches=['-q', '-n'], input = 'set list on; select mon$crypt_state from mon$database; commit; DROP DATABASE;', combine_output=True)

        assert act_tmp.clean_stdout == act_tmp.clean_expected_stdout
        act_tmp.reset()
        assert act_tmp.db.db_path.is_file(), f'File {str(act_tmp.db.db_path)} was unexpectedly removed from disk!'

    #< with tmp_log.open('w') as f_log




