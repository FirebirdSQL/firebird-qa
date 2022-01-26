#coding:utf-8

"""
ID:          issue-6034
ISSUE:       6034
TITLE:       Restore (without replace) when database already exists crashes gbak or Firebird (when run through service manager)
DESCRIPTION:
JIRA:        CORE-5771
"""

import pytest
from difflib import unified_diff
from pathlib import Path
from firebird.qa import *

substitutions = [('database .*tmp_core_5771.fdb already exists.',
                  'database tmp_core_5771.fdb already exists.'),
                 ('opened file .*tmp_core_5771.fbk', 'opened file tmp_core_5771.fbk')]

db = db_factory()

act = python_act('db', substitutions=substitutions)

expected_stdout = """
    gbak:opened file tmp_core_5771.fbk
"""

expected_stderr = """
database tmp_core_5771.fdb already exists.  To replace it, use the -REP switch
-Exiting before completion due to errors
"""

fbk_file = temp_file('tmp_core_5771.fbk')
fdb_file = temp_file('tmp_core_5771.fdb')

@pytest.mark.version('>=4.0')
def test_1(act: Action, fbk_file: Path, fdb_file: Path):
    act.gbak(switches=['-b', act.db.dsn, str(fbk_file)])
    act.gbak(switches=['-rep', str(fbk_file), act.get_dsn(fdb_file)])
    #
    log_before = act.get_firebird_log()
    #
    act.reset()
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.svcmgr(switches=['action_restore', 'bkp_file', str(fbk_file),
                         'dbname', str(fdb_file), 'verbose'])
    #
    log_after = act.get_firebird_log()
    assert list(unified_diff(log_before, log_after)) == []
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
