#coding:utf-8

"""
ID:          issue-7647
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7647
TITLE:       Regression: Error in isc_array_lookup_bounds
DESCRIPTION:
NOTES:
    [23.03.2024] pzotov
    Checked on 3.0.12.33735, 4.0.5.3077 - works fine.
    REGRESSION STILL EXISTS on 5.0.1.1368, 6.0.0.299: got exception
    "ValueError: Incorrect ARRAY field value." raises on firebird.driver: 1.10.1 / firebird-qa-0.19.2
    Added restriction for major versions that are allowed to be checked: currently only 3.x and 4.x.
    See also: https://github.com/FirebirdSQL/firebird/issues/7862

    [21.07.2024] pzotov
    Problem with 6.x has been fixed in 6.0.0.346, commit date 07.05.2024:
    https://github.com/FirebirdSQL/firebird/commit/17b007d14f8ccc6cfba0d63a3b2f21622ced20d0
    Removed upper limit restriction for major version.
"""

import pytest
from firebird.qa import *

db = db_factory(init = 'create table array_table (a int[3,4]);')

expected_stdout = """
    [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
"""

act = python_act('db')

@pytest.mark.version('>=3.0.12')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        cur = con.cursor()

        arrayIn = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9,10,11,12]
          ]

        cur.execute("insert into array_table values (?)", (arrayIn,))
        con.commit()

        cur.execute("select a from array_table")
        arrayOut = cur.fetchone()[0]
        print(f"{arrayOut}")

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
