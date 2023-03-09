#coding:utf-8

"""
ID:          issue-2727
ISSUE:       2727
TITLE:       Include PLAN in mon$statements
DESCRIPTION:
JIRA:        CORE-2303
FBTEST:      bugs.core_2303
"""

import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db')

TAG_TEXT = 'TAG_FOR_SEARCH'
expected_stdout = f"""
    select 1 /* {TAG_TEXT} */ from rdb$database
    Select Expression
        -> Table "RDB$DATABASE" Full Scan
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        cur1 = con.cursor()
        cur2 = con.cursor()
        ps = cur1.prepare(f'select 1 /* {TAG_TEXT} */ from rdb$database')
        cur2.execute(f"select mon$sql_text, mon$explained_plan from mon$statements s where s.mon$sql_text containing '{TAG_TEXT}' and s.mon$sql_text NOT containing 'mon$statements'")
        for r in cur2:
            print(r[0])
            print(r[1])

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
