#coding:utf-8
#
# id:           functional.intfunc.date.datediff_07
# title:        test de la fonction datediff pour avoir le resultat en minute
# decription:   Returns an exact numeric value representing the interval of time from the first date/time/timestamp value to the second one.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.intfunc.date.datediff_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set list on;
    select datediff( millisecond,
                     cast( '01.01.0001 00:00:00.0001' as timestamp),
                     cast( '31.12.9999 23:59:59.9999' as timestamp)
                   ) as dd_01a from rdb$database;

    select datediff( millisecond,
                     time '00:00:00.0001',
                     time '23:59:59.9999'
                   ) as dd_01b from rdb$database;


    select datediff( millisecond
                     from cast( '01.01.0001 00:00:00.0001' as timestamp)
                     to cast( '31.12.9999 23:59:59.9999' as timestamp)
                   ) as dd_02a from rdb$database;

    select datediff( millisecond
                     from cast( '00:00:00.0001' as time)
                     to cast( '23:59:59.9999' as time)
                   ) as dd_02b from rdb$database;
  
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DD_01A                          315537897599999.8
    DD_01B                          86399999.8
    DD_02A                          315537897599999.8
    DD_02B                          86399999.8
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

