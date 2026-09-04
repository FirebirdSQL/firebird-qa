#coding:utf-8

"""
ID:          n/a
TITLE:       gbak utility: changing write mode to sync/async must be prohibited when access mode is read-only
DESCRIPTION:
    Along with check what TOTLE says, this test also verifies that runtime error now is supplied with detailed message,
    namely: 'attempted update on read-only database'.
    Before merge of https://github.com/FirebirdSQL/firebird-qa/pull/36 ('Add error text output for utilities to firebird-qa')
    this detailed message could be seen only if FB utility was called with combine_output = True.
    Merge was 15.09.2025, https://github.com/FirebirdSQL/firebird-qa/commit/0863a3ce43096289eaba6d6bc37bb2ff488d61f8
NOTES:
    [04.09.2026] pzotov
    Checked on 6.0.0.2169; 5.0.5.1879; 4.0.8.3314; 3.0.15.33884.
"""
import pytest
from firebird.qa import *

db = db_factory(charset='UTF8', utf8filename = True)
act = python_act('db')

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):

    act.expected_stdout = """
        gfix execution failed
        attempted update on read-only database
    """
    act.gfix(switches = ['-mode', 'read_only', act.db.dsn])
    try:
        act.gfix(switches = ['-write', 'sync', act.db.dsn])
    except ExecutionError as e:
        print(e.__str__())

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
