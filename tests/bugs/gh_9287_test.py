#coding:utf-8

"""
ID:          issue-9287
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9287
TITLE:       Incorrect 'Table unknown' error positions in INSERT and UPDATE OR INSERT
DESCRIPTION:
NOTES:
    [26.11.2026] pzotov
    Confirmed problem on 6.0.0.2469-e0ab074.
    Checked on 6.0.0.2516-1982b96.
"""
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail OFF;
    insert into 











        unknown_table(id) values(1);

    update or insert into 













         unknown_table(id, x) values(1, 100) matching (x);
"""

substitutions = [
     ('[ \t]+', ' ')
    ,('(-)?At line (0|1), column (0|1)', 'INVALID ROW/COL POSITION IS REPORTED.')
    ,('(-)?At line {2,}, column {2,}', 'Valid row/col position is reported.')
]

act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    Statement failed, SQLSTATE = 42S02
    Dynamic SQL Error
    -SQL error code = -204
    -Table unknown
    -"UNKNOWN_TABLE"
    -At line 13, column 9
    Statement failed, SQLSTATE = 42S02
    Dynamic SQL Error
    -SQL error code = -204
    -Table unknown
    -"UNKNOWN_TABLE"
    -At line 15, column 10
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
