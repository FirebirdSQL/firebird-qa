#coding:utf-8
#
# id:           functional.intfunc.date.dateadd_07
# title:        test de la fonction dateadd  pour l'ajout d'une seconde
# decription:   Returns a date/time/timestamp value increased (or decreased, when negative) by the specified amount of time.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.date.dateadd_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = [('^((?!sqltype:|DD_).)*$', ''), ('[ \t]+', ' '), ('.*alias:.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set sqlda_display on;
    select dateadd(-1 second to time '12:12:00' ) as tx_1  from rdb$database;
    select dateadd(second,-1, time '12:12:00' ) as tx_2 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 560 TIME scale: 0 subtype: 0 len: 4
    TX_1                            12:11:59.0000

    01: sqltype: 560 TIME scale: 0 subtype: 0 len: 4
    TX_2                            12:11:59.0000
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

