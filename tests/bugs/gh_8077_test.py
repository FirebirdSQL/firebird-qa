#coding:utf-8

"""
ID:          issue-8077
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8077
TITLE:       Error "Too many recursion levels" does not stop execuition of code that uses ON DISCONNECT trigger (FB 4.x+)
DESCRIPTION:
    Test creates DB-triggers 'ON CONNECT' and 'ON DISCONNECT', plus table 'LOG' for logging actions performed by DB-triggers.
    Trigger 'ON DISCONNECT' makes EDS with new role thus creating new connection which will then be immediately finished and,
    in turn, fire again this trigger. Eventually this must cause ISQL to terminate and firebird.log must contain errors.
    Difference between old and new firebird.log must contain exactly two errors about detahc problem
    (Error at disconnect: / Execute statement error at attach : / 335544830 : Too many recursion levels of EXECUTE STATEMENT)
NOTES:
    [27.05.2024] pzotov
    Time of ISQL execution is limited by MAX_WAIT_FOR_ISQL_TERMINATE seconds. Currently it is ~6s for SS and ~18s for CS.

    Checked on 6.0.0.362, 5.0.1.1408, 4.0.5.3103 (all SS/CS).
"""

import re
from difflib import unified_diff
import pytest
import time
from pathlib import Path
import subprocess
import locale

import firebird.driver
from firebird.qa import *

db = db_factory()
substitutions = [
                    ('^((?!(E|e)rror|statement|recursion|source|rdb_trg|trigger|ext_pool_active|isql_outcome).)*$', '')
                    ,('Execute statement error.*', 'Execute statement error')
                    ,('Firebird::.*', 'Firebird::')
                    ,('line(:)?\\s+\\d+.*', '')
                    ,('[ \t]+', ' ')
                ]
act = python_act('db', substitutions = substitutions)

tmp_sql = temp_file('tmp_8077.sql')
tmp_log = temp_file('tmp_8077.log')

MAX_WAIT_FOR_ISQL_BEGIN_WORK=0.5
MAX_WAIT_FOR_ISQL_TERMINATE=30

#--------------------------------------------------------------------

@pytest.mark.version('>=4.0.5')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path, capsys):

    test_sql = f"""
        set list on;
        set bail on;

        set term ^;
        create or alter trigger trg_attach on connect as begin end
        ^
        recreate table log( att bigint default current_connection, event_name varchar(6) )
        ^
        create or alter trigger trg_attach on connect as
            declare v_pool_size int;
        begin
            in autonomous transaction do
            insert into log(event_name) values ('attach');
        end
        ^
        create or alter trigger trg_detach on disconnect as
        begin
            execute statement ('insert into log(event_name) values(?)') ('detach')
            with autonomous transaction
            on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
                as user '{act.db.user}' password '{act.db.password}' role 'R' || replace(uuid_to_char(gen_uuid()),'-','')
            ;
        end
        ^
        set term ;^
        commit;
        select
            rdb$trigger_name as "rdb_trg_name"
            ,rdb$trigger_type as "rdb_trg_type"
        from rdb$triggers
        where rdb$system_flag is distinct from 1
        order by rdb$trigger_name;
        rollback;
        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';
        select cast(rdb$get_context('SYSTEM', 'EXT_CONN_POOL_SIZE') as int) as "ext_pool_size_1" from rdb$database;
        quit;
    """
    with open(tmp_sql, 'w') as f:
        f.write(test_sql)

    # Get Firebird log before test
    # ----------------------------
    fb_log_init = act.get_firebird_log()
    failed_finish_isql_msg = ''
    with act.db.connect() as con:
        with open(tmp_log, 'w') as f:
            try:
                p_handed_isql = subprocess.Popen( [act.vars['isql'], '-i', str(tmp_sql),
                                                  '-user', act.db.user,
                                                  '-password', act.db.password, act.db.dsn],
                                                  stdout = f,
                                                  stderr = subprocess.STDOUT
                                                )

                for i in range(MAX_WAIT_FOR_ISQL_TERMINATE):
                    time.sleep(1)
                    # Check if child process has terminated.
                    # Set and return returncode attribute. Otherwise, returns None.
                    if p_handed_isql.poll() is not None:
                        break

            finally:
                p_handed_isql.terminate()

            if p_handed_isql.poll() is None:
                failed_finish_isql_msg = f'isql_outcome: process WAS NOT terminated in {MAX_WAIT_FOR_ISQL_TERMINATE} second. Probably MAX_WAIT_FOR_ISQL_TERMINATE value must be increased.'
        
    # Get Firebird log after test
    # ----------------------------
    fb_log_curr = act.get_firebird_log()

    with open(tmp_log, 'a') as f:
        if failed_finish_isql_msg:
            f.write(failed_finish_isql_msg+'\n')
        for line in unified_diff(fb_log_init, fb_log_curr):
            if line.startswith('+'):
                f.write(line[1:] + '\n')


    expected_stdout = f"""
        rdb_trg_name                    TRG_ATTACH
        rdb_trg_type                    8192
        rdb_trg_name                    TRG_DETACH
        rdb_trg_type                    8193
        
        Error at disconnect:
        Execute statement error at attach :
        335544830 : Too many recursion levels of EXECUTE STATEMENT
        Data source : Firebird::
        At trigger 'TRG_DETACH'

        Error at disconnect:
        Execute statement error at attach :
        335544830 : Too many recursion levels of EXECUTE STATEMENT
        Data source : Firebird::
        At trigger 'TRG_DETACH'
    """

    with open(tmp_log, 'r') as f:
        for line in f:
            print(line)

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
