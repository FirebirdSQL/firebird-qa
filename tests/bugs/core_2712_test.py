#coding:utf-8

"""
ID:          issue-3109
ISSUE:       3109
TITLE:       Do not print "invalid request BLR" for par.cpp errors with valid BLR
DESCRIPTION:
JIRA:        CORE-2712
FBTEST:      bugs.core_2712
NOTES:
    [26.06.2025] pzotov
    Re-implemented via try/except and check show exception data.
    Suppressing quotes around `id <...>` as irrelevant to this test.
    Checked on 6.0.0.876; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813.
    [05.03.2026] pzotov
    Adjusted expected output which has changed since #b38046e1 ('Encapsulation of metadata cache'; 24-feb-2026 17:31:04 +0000).
    Checked on 6.0.0.1807-46797ab.
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()

substitutions = [('table (")?id \\d+(")? is not defined', 'table is not defined')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        cur1 = con.cursor()
        cur1.execute("recreate table test(x int)")
        con.commit()
        cur1.execute("insert into test values(1)")
        con.commit()
        ps = None
        try:
            with act.db.connect() as con2:
                cur2 = con2.cursor()
                cur2.execute("select 1 from rdb$database")
                cur1.execute("drop table test")
                ps = cur2.prepare("update test set x=-x")
                con2.commit()
        except DatabaseError as e:
            print(e.__str__())
            for x in e.gds_codes:
                print(x)
        finally:
            if ps:
                ps.free()

    expected_stdout_5x = """
        table is not defined
        335544395
    """

    expected_stdout_6x = """
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
