#coding:utf-8

"""
ID:          issue-5985
ISSUE:       5985
TITLE:       FB >= 3 crashes when restoring backup made by FB 2.5
DESCRIPTION:
JIRA:        CORE-5719
FBTEST:      bugs.core_5719
NOTES:
    [14.04.2026] pzotov
    Confirmed bug on 3.0.3.32886 (20-jan-2018):
    1. Log of restore (when 'gbak -v' is used) contained:
      ...
      gbak: ERROR:Error reading data from the connection.
      gbak:Exiting before completion due to errors
    2. firebird.log contained:
      REMOTE INTERFACE/gds__detach: Unsuccesful detach from database.
      Uncommitted work may have been lost.
      Error writing data to the connection.
    Database validation does NOT show any problem. No sense to check its output.

    Refactored check of error messages in restore log.
    The firebird.log must be checked more strictly - it may contain somewhat irrelated to crash:
        INET/inet_error: send errno = 10054, server host = localhost, address
        INET/inet_error: read errno = 10054, server host = 192.0.2.1, address
    This test also present in GTCS list, see it here:
    https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/SV_HIDDEN_VAR_2_5.script

    Checked on 6.0.0.1891; 5.0.4.1808; 4.0.7.3269; 3.0.14.33855
"""
import locale
import re
import pytest
import zipfile
from difflib import unified_diff
from pathlib import Path
from firebird.qa import *
from firebird.driver import SrvRestoreFlag

db = db_factory()

act = python_act('db')

tmp_fbk = temp_file('core5719-ods-11_2.fbk')
tmp_fdb = temp_file('check_restored_5719.fdb')

@pytest.mark.version('>=3.0.3')
def test_1(act: Action, tmp_fbk: Path, tmp_fdb: Path, capsys):
    zipped_fbk_file = zipfile.Path(act.files_dir / 'core_5719-ods-11_2.zip',
                                   at='core5719-ods-11_2.fbk')
    tmp_fbk.write_bytes(zipped_fbk_file.read_bytes())

    allowed_patterns = [  re.compile('gbak:\\s*Exiting before completion',re.IGNORECASE),
                          re.compile('Error\\s+(reading|writing)',re.IGNORECASE),
                       ]
    #--------------------------------------------------------
    log_before = act.get_firebird_log()
    act.gbak( switches=['-rep', '-v', tmp_fbk, 'localhost:'+str(tmp_fdb) ], combine_output = True, io_enc = locale.getpreferredencoding() )
    log_after = act.get_firebird_log()
    #--------------------------------------------------------

    # 1. Check that restore does not contain messages related to crash:
    for line in act.stdout.splitlines():
            if act.match_any(line.strip(), allowed_patterns):
                print('UNEXPECTED result of restore:',line)
    act.reset()
    #--------------------------------------------------------
    # 2. Check that firebird.log has no [new] messages about crash:
    for line in list(unified_diff(log_before, log_after)):
        if act.match_any(line.strip(), allowed_patterns):
            print('UNEXPECTED message in firbird.log:',line)
    act.reset()

    act.expected_stdout = ''
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
