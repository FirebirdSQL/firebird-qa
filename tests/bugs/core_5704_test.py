#coding:utf-8

"""
ID:          issue-5970
ISSUE:       5970
TITLE:       Avoid UPDATE of RDB$DATABASE by ALTER DATABASE statement when possible
DESCRIPTION:
  Instead of doing 'nbackup -L' plus fill database with lot of new data and then 'nbackup -N' with waiting for
  delta will be integrated into main file, we can get the same result by invoking 'alter database add difference file'
  statement in the 1st attachment in RC NO_REC_VERS and WITHOUT COMMITTING it, and then attempt to establish new connect
  using ES/EDS. Second attachment should be made without any problem, despite that transaction in 1st connect not yet
  committed or rolled back.

  Confirmed lock of rdb$database record (which leads to inability to establish new connect) on WI-V3.0.3.32837.
JIRA:        CORE-5704
"""

import pytest
import subprocess
import time
from pathlib import Path
from firebird.qa import *
from firebird.driver import ShutdownMode, ShutdownMethod

db = db_factory()

act = python_act('db')

expected_stdout = """
    CHECK_EDS_RESULT                1
    Records affected: 1
    Records affected: 0
    CHECK_EDS_RESULT                1
    Records affected: 1
    Records affected: 0
"""

eds_script = temp_file('eds_script.sql')
eds_output = temp_file('eds_script.out')
new_diff_file = temp_file('_new_diff_5704.tmp')
new_main_file = temp_file('new_main_5704.tmp')

@pytest.mark.version('>=3.0.3')
def test_1(act: Action, eds_script: Path, eds_output: Path, new_diff_file: Path,
           new_main_file: Path):
    eds_script.write_text(f"""
    set count on;
    set list on;
    set autoddl off;

    set term ^;
    create or alter procedure sp_connect returns(check_eds_result int) as
       declare usr varchar(31);
       declare pwd varchar(31);
       declare v_sttm varchar(255) = 'select 1 from rdb$database';
    begin
       usr ='{act.db.user}';
       pwd = '{act.db.password}';
       execute statement v_sttm
       on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
       as user usr password pwd
       into check_eds_result;
       suspend;
    end
    ^
    set term ^;

    commit;
    set transaction read committed no record_version lock timeout 1;

    alter database add difference file '{new_diff_file}';
    select * from sp_connect;

    rollback;
    select * from rdb$files;
    rollback;

    set transaction read committed no record_version lock timeout 1;

    alter database add file '{new_main_file}';
    select * from sp_connect;
    --select * from rdb$files;
    rollback;
    select * from rdb$files;
    """)
    #
    with open(eds_output, mode='w') as eds_out:
        p_eds_sql = subprocess.Popen([act.vars['isql'], '-i', str(eds_script),
                                      '-user', act.db.user,
                                      '-password', act.db.password, act.db.dsn],
                                     stdout=eds_out, stderr=subprocess.STDOUT)
        try:
            time.sleep(4)
        finally:
            p_eds_sql.terminate()
    # Ensure that database is not busy
    with act.connect_server() as srv:
        srv.database.shutdown(database=act.db.db_path, mode=ShutdownMode.FULL,
                              method=ShutdownMethod.FORCED, timeout=0)
        srv.database.bring_online(database=act.db.db_path)
    # Check
    act.expected_stdout = expected_stdout
    act.stdout = eds_output.read_text()
    assert act.clean_stdout == act.clean_expected_stdout
