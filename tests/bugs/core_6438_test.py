#coding:utf-8

"""
ID:          issue-2366
ISSUE:       2366
TITLE:       ISQL: bad headers when text columns has >= 80 characters
DESCRIPTION:
JIRA:        CORE-6438
FBTEST:      bugs.core_6438
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
hdr_len: 65533
txt_len: 65533
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, capsys):
    data = '1' * 65533
    act.isql(switches=[], input=f'''select '{data}' as " ", 1 as "  " from rdb$database;''')
    for line in act.stdout.splitlines():
        if line.startswith('='):
            hdr_len = len(line.split()[0])
        elif line.startswith('1'):
            txt_len = len(line.split()[0])
    print('hdr_len:', hdr_len)
    print('txt_len:', txt_len)
    #
    act.reset()
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
