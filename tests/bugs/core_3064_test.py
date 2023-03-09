#coding:utf-8

"""
ID:          issue-3443
ISSUE:       3443
TITLE:       Using both the procedure name and alias inside an explicit plan crashes the server
DESCRIPTION:
JIRA:        CORE-3064
FBTEST:      bugs.core_3064
NOTES:
    [04.03.2023] pzotov
    Expected output was splitted because FB 5.x now *allows* execution w/o error.
"""

import pytest
from firebird.qa import *

init_script = """
    set term ^ ;
    create or alter procedure get_dates (
        adate_from date,
        adate_to date )
    returns (
        out_date date )
    as
      declare variable d date;
    begin
      d = adate_from;
      while (d<=adate_to) do
        begin
          out_date = d;
          suspend;
          d = d + 1;
        end
    end^
    set term ; ^
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set planonly;
    select * from get_dates( 'yesterday', 'today' ) PLAN (GET_DATES NATURAL);
    select * from get_dates( 'yesterday', 'today' ) p PLAN (P NATURAL);
"""

act = isql_act('db', test_script, substitutions=[('offset .*', 'offset')])

fb3x_expected_out = """
    Statement failed, SQLSTATE = 42S02
    Dynamic SQL Error
    -SQL error code = -104
    -Invalid command
    -there is no alias or table named GET_DATES at this scope level

    Statement failed, SQLSTATE = HY000
    invalid request BLR at offset 50
    -BLR syntax error: expected TABLE at offset 51, encountered 132
"""

fb5x_expected_out = """
    PLAN (GET_DATES NATURAL)
    PLAN (P NATURAL)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = fb3x_expected_out if act.is_version('<5') else fb5x_expected_out
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
