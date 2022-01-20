#coding:utf-8

"""
ID:          issue-1734
ISSUE:       1734
TITLE:       Data type unknown
DESCRIPTION:
JIRA:        CORE-1315
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """COALESCE
-----------
2

COALESCE
-----------
1
"""

@pytest.mark.version('>=3')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        c = con.cursor()
        statement = c.prepare('select coalesce(?,1) from RDB$DATABASE')
        c.execute(statement,[2])
        act.print_data(c)
        c.execute(statement,[None])
        act.print_data(c)
        act.stdout = capsys.readouterr().out
        act.expected_stdout = expected_stdout
        assert act.clean_stdout == act.clean_expected_stdout


