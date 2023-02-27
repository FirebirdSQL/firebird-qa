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
  As far as query will return columd value = 3 ("is encrypting") - we break from loop and try to DROP database
  using method drop_database() of class Connection.
  Otherwise, if we could not find this state during <ENCRYPTION_START_MAX_WAIT> seconds, assert will interrupt further execution.

  Attempt to drop database which has incompleted encryption must raise exception:
      lock time-out on wait transaction
      -object is in use
  Test verifies that this exception actually raises (i.e. this is EXPECTED behaviour).

NOTES:
    [27.02.2023] pzotov
    0. SuperServer only was affected. No such problem on Classic.
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
from firebird.driver import DatabaseError

FLD_LEN =   500
N_ROWS = 100000
ENCRYPTION_START_MAX_WAIT = 30

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

    max_encrypt_decrypt_ms = int(enc_settings['max_encrypt_decrypt_ms']) # 5000
    encryption_plugin = enc_settings['encryption_plugin'] # fbSampleDbCrypt
    encryption_holder  = enc_settings['encryption_holder'] # fbSampleKeyHolder
    encryption_key = enc_settings['encryption_key'] # Red

    sttm = f'alter database encrypt with "{encryption_plugin}" key "{encryption_key}";'
    tmp_sql.write_bytes(sttm.encode('utf-8'))

    with act_tmp.db.connect() as con_killer:
        cur_check_mon = con_killer.cursor()
        ps = cur_check_mon.prepare('select mon$crypt_state from mon$database') # 0 = non-encrypted; 1 = encrypted; 2 = is DEcrypting; 3 - is Encrypting
        encryption_started = False
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
            i = 0
            while True:
                cur_check_mon.execute(ps)
                for r in cur_check_mon:
                    db_crypt_state = r[0]

                con_killer.commit()

                if db_crypt_state == 3:
                    encryption_started = True
                    cur_check_mon.call_procedure('sp_tmp', ('encryption_started',))
                    break
                elif i > ENCRYPTION_START_MAX_WAIT:
                    break

                time.sleep(1)

            assert encryption_started, f'Could not find start of encryption process for {ENCRYPTION_START_MAX_WAIT} seconds.'

            try:
                cur_check_mon.call_procedure('sp_tmp', ('before drop database',))
                cur_check_mon.close()
                #time.sleep(1)
                # act_tmp.db.drop_database()
                con_killer.drop_database()
            except Exception as e:
                print(e)
        #< with tmp_log.open('w') as f_log
    #< with act_tmp.db.connect() as con_killer

    drop_db_expected_stdout = """
        lock time-out on wait transaction
        -object is in use
    """

    act_tmp.expected_stdout = drop_db_expected_stdout
    act_tmp.stdout = capsys.readouterr().out
    assert act_tmp.clean_stdout == act_tmp.clean_expected_stdout
    act_tmp.reset()
