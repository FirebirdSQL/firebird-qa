#coding:utf-8

"""
ID:          issue-5255
ISSUE:       5255
JIRA:        CORE-4964
FBTEST:      bugs.core_4964
TITLE:       Real errors during connect to security database are hidden by Srp user manager.
  Errors should be logged no matter what AuthServer is used
DESCRIPTION:

    Test does following:
    1) creates temporary user using plugin Srp (in order to avoid occasional connect as SYSDBA using Legacy plugin);
    2) makes copy of DB to temporary file (<tmp_fdb>; we will try to connect to it via ALIAS from databases.conf);
    3) makes copy ot databases.conf (for restoring from it at the end) and adds following lines in it:
        <tmp_alias> = <tmp_fdb>
        {
            SecurityDatabase = $(dir_conf)/firebird.msg
        }

    NOTE: we intentionally assign to SecurityDatabase value that points to the file
    that for sure exists but is INVALID for usage as fdb: 'firebird.msg'

    Then we:
    1) obtain content of server firebird.log
    2) try to make connect to alias <tmp_alias> and (as expected) get error.
    3) wait a little and obtain again content of server firebird.log

    Finally we restore original databases.conf and check client error messages and diff in the firebird.log

NOTES:
    [30.05.2022] pzotov
    Alias <tmp_alias> must NOT refer to test DB, otherwise test fails with duplicate(?) issuing DatabaseError.
    To be discussed with pcisar, comments will be updated soon.

    Checked on 5.0.0.501, 4.0.1.2692, 3.0.8.33535
"""
import os
import pytest
from firebird.qa import *
import locale
from pathlib import Path
import shutil
import datetime
import time
from difflib import unified_diff
import re

substitutions = [('file .* is not a valid database', 'file is not a valid database'), ]

db = db_factory(utf8filename=True, charset='UTF8')
act = python_act('db', substitutions=substitutions)
tmp_user = user_factory('db', name='tmp$c4964', password='123', plugin = 'Srp')

expected_stdout_isql = """
    Statement failed, SQLSTATE = 08006
    Error occurred during login, please check server firebird.log for details
"""

expected_stdout_log_diff = """
    Authentication error
    file is not a valid database
"""

dbconf_bak = temp_file('dbconf.bak')
tmp_fdb = temp_file('tmp_4964_fdb.tmp')

@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_user: User, dbconf_bak: Path, tmp_fdb: Path, capsys):
    with act.connect_server() as srv:
        srv_home=str(srv.info.home_directory)

    dbconf_cur = Path(srv_home, 'databases.conf')
    shutil.copyfile(dbconf_cur, Path(dbconf_bak))

    with act.connect_server(encoding=locale.getpreferredencoding()) as srv:
        srv.info.get_log()
        fb_log_init = srv.readlines()
    
    try:
        shutil.copyfile(act.db.db_path, tmp_fdb)

        tmp_alias = 'tmp_4964_' + datetime.datetime.now().strftime("%H%M%S")
        addi_lines = f"""
            # Temporary added by QA, test CORE-4964. Should be removed auto.
            ###########
            {tmp_alias} = {str(tmp_fdb)} {{
            # {tmp_alias} = {act.db.db_path} {{
                # dir_msg - directory where messages file (firebird.msg) is located
                SecurityDatabase = $(dir_msg)/firebird.msg
            }}
        """
        with open(dbconf_cur, mode = 'a') as f:
            f.seek(0, 2)
            f.write(addi_lines)

        act.isql(switches=['-q', act.get_dsn(tmp_alias), '-user', tmp_user.name, '-password', tmp_user.password], input = 'select mon$database_name from mon$database;', credentials = False, connect_db = False, combine_output = True, io_enc=locale.getpreferredencoding())

    finally:
        shutil.copyfile(Path(dbconf_bak), dbconf_cur)


    time.sleep(1)
    with act.connect_server(encoding=locale.getpreferredencoding()) as srv:
        srv.info.get_log()
        fb_log_curr = srv.readlines()

    act.expected_stdout = expected_stdout_isql
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

    diff_patterns = [
        r"\+\s+Authentication error",
        r"\+\s+file .* is not a valid database",
    ]
    diff_patterns = [re.compile(s) for s in diff_patterns]

    for line in unified_diff(fb_log_init, fb_log_curr):
        if line.startswith('+'):
            if act.match_any(line, diff_patterns):
                print(line[1:].strip())

    act.expected_stdout = expected_stdout_log_diff
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
