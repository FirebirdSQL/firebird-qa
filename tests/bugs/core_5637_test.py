#coding:utf-8

"""
ID:          issue-5903
ISSUE:       5903
TITLE:       string right truncation on restore of security db
DESCRIPTION:
NOTES:
[25.10.2019] Refactored
  restored DB state must be changed to full shutdown in order to make sure tha all attachments are gone.
  Otherwise got on CS: "WindowsError: 32 The process cannot access the file because it is being used by another process".
JIRA:        CORE-5637
"""

import pytest
import zipfile
from difflib import unified_diff
from pathlib import Path
from firebird.qa import *
from firebird.driver import SrvRestoreFlag

db = db_factory()

act = python_act('db')

sec_fbk = temp_file('core5637-security3.fbk')
sec_fdb = temp_file('core5637-security3.fdb')

@pytest.mark.version('>=4.0')
def test_1(act: Action, sec_fbk: Path, sec_fdb: Path):
    zipped_fbk_file = zipfile.Path(act.files_dir / 'core_5637.zip', at='core5637-security3.fbk')
    sec_fbk.write_bytes(zipped_fbk_file.read_bytes())
    #
    log_before = act.get_firebird_log()
    # Restore security database
    with act.connect_server() as srv:
        srv.database.restore(database=sec_fdb, backup=sec_fbk, flags=SrvRestoreFlag.REPLACE)
        restore_log = srv.readlines()
        #
        log_after = act.get_firebird_log()
        #
        srv.database.validate(database=sec_fdb)
        validation_log = srv.readlines()
    #
    assert [line for line in restore_log if 'ERROR' in line.upper()] == []
    assert [line for line in validation_log if 'ERROR' in line.upper()] == []
    assert list(unified_diff(log_before, log_after)) == []
