#coding:utf-8

"""
ID:          issue-6785
ISSUE:       6785
TITLE:       Problem when restoring the database on FB 4.0 RC1 (gbak regression)
DESCRIPTION:
    Test used database backup that was provided in the ticket.

    Maximal allowed time is set here for restoring process and gbak will be
    forcedly killed if it can not complete during this time.
    Currently this time is 300 seconds (see 'MAX_THRESHOLD' variable).

    Database is validated (using 'gfix -v -full') after successful restore finish.
    Test checks that returned codes for both gbak and validation are zero.

    Restore issues warnings:
      gbak: WARNING:function F_DATETOSTR is not defined
      gbak: WARNING:    module name or entrypoint could not be found
      gbak: WARNING:function F_DATETOSTR is not defined
      gbak: WARNING:    module name or entrypoint could not be found
    All of them are ignored by this test when gbak output is parsed.

    Confirmed bug on 4.0.0.2452 SS: gbak infinitely hanged.
    Checked on 4.0.0.2453 SS/CS (Linux and Windows): all OK, restore lasts near 200s.
FBTEST:      bugs.gh_6785
NOTES:
    [30.06.2022] pzotov
    Checked on 4.0.1.2692, 5.0.0.509. Re-check reproducing of problem on 4.0.0.2452.
    ::: NB-1 :::
    DO NOT forget to specify 'encoding=locale.getpreferredencoding()' otherwise attempt to get content
    of firebird.log can fail if it contains non-ascii messages, e.g. "Невозможно создать файл ..." etc.
    In this case act.get_firebird_log() will raise:
    UnicodeDecodeError: 'ascii' codec can't decode byte 0x** in position ***: ordinal not in range(128)
    ::: NB-2 :::
    Currently one can NOT use 'act.get_firebird_log()' to get content of FB log with non-ascii messages.
    We have to use 'with act.connect_server(encoding=locale.getpreferredencoding()) as srv' and then
    work with it like this: 'srv.info.get_log(); fblog = srv.readlines()'.
    This code may be changed / adjusted after.
"""

import locale
import zipfile
import subprocess
import re

import pytest
from firebird.qa import *
from firebird.driver import SrvRepairFlag
from pathlib import Path
from difflib import unified_diff
import time

db = db_factory()
act = python_act('db')

tmp_log = temp_file('gh_6785.tmp.log')
tmp_fbk = temp_file('gh_6785.tmp.fbk')
tmp_fdb = temp_file('gh_6785.tmp.fdb')

###################
MAX_THRESHOLD = 300
###################

expected_stdout = """
    Restore retcode: 0
    Validation retcode: 0
"""

restore_completed_msg = 'Restore COMPLETED.'

@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_fbk: Path, tmp_fdb: Path, tmp_log: Path, capsys):
    zipped_fbk_file = zipfile.Path(act.files_dir / 'gh_6785.zip', at = 'gh_6785.fbk')
    tmp_fbk.write_bytes(zipped_fbk_file.read_bytes())

    restore_code = -1

    # ...\gbak.exe -rep ...\gh_6785.tmp.fbk localhost:...\gh_6785.tmp.fdb -st tdrw -v -y ...\gh_6785.tmp.log
    # If the timeout expires, the child process will be killed and waited for.
    # The TimeoutExpired exception will be re-raised after the child process has terminated.
    try:
        p = subprocess.run([ act.vars['gbak'],
                            '-user', act.db.user, '-password', act.db.password,
                            '-rep', tmp_fbk, tmp_fdb,
                            '-st', 'tdrw', 
                            '-v', '-y', str(tmp_log)
                          ]
                          ,stderr = subprocess.STDOUT
                          ,timeout = MAX_THRESHOLD
                         )
        print( restore_completed_msg )
        restore_code = p.returncode

    except Exception as e:
        print(e.__str__())
        tmp_fdb.unlink()

    act.expected_stdout = restore_completed_msg
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

    if restore_code == 0:
        
        # Get FB log before validation, run validation and get FB log after it:
        with act.connect_server(encoding=locale.getpreferredencoding()) as srv:

            # CURRENTLY CAN NOT USE THIS: fblog_1 = act.get_firebird_log()
            srv.info.get_log()
            fblog_1 = srv.readlines()

            srv.database.repair(database = str(tmp_fdb), flags=SrvRepairFlag.CORRUPTION_CHECK)

            # CURRENTLY CAN NOT USE THIS: fblog_2 = act.get_firebird_log()
            srv.info.get_log()
            fblog_2 = srv.readlines()

            p_diff = re.compile('Validation finished: \\d+ errors, \\d+ warnings, \\d+ fixed')
            validation_result = ''
            for line in unified_diff(fblog_1, fblog_2):
                if line.startswith('+') and p_diff.search(line):
                    validation_result =line.strip().replace('\t', ' ')
                    break


            assert validation_result == '+ Validation finished: 0 errors, 0 warnings, 0 fixed'
            act.reset()
