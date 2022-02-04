#coding:utf-8

"""
ID:          intfunc.date.dateadd-07
TITLE:       DATEADD
DESCRIPTION:
  Returns a date/time/timestamp value increased (or decreased, when negative) by the specified amount of time.
FBTEST:      functional.intfunc.date.dateadd_07
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set sqlda_display on;
    select dateadd(-1 second to time '12:12:00' ) as tx_1  from rdb$database;
    select dateadd(second,-1, time '12:12:00' ) as tx_2 from rdb$database;
"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype:|DD_).)*$', ''),
                                                 ('[ \t]+', ' '), ('.*alias:.*', '')])

expected_stdout = """
    01: sqltype: 560 TIME scale: 0 subtype: 0 len: 4
    TX_1                            12:11:59.0000

    01: sqltype: 560 TIME scale: 0 subtype: 0 len: 4
    TX_2                            12:11:59.0000
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
