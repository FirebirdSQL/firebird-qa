#coding:utf-8
#
# id:           bugs.core_5750
# title:        Date-time parsing is very weak
# decription:   
#                   Checked on: 4.0.0.1479: OK, 1.263s.
#               
#                   27.10.2020.
#                   Parser changed after following fixes:
#                       - CORE-6427 - Whitespace as date separator causes conversion error.
#                       - CORE-6429 - Timezone offset in timestamp/time literal and CAST should follow SQL standard syntax only.
#                   See: https://github.com/FirebirdSQL/firebird/commit/ff37d445ce844f991242b1e2c1f96b80a5d1636d
#                   Adjusted expected stdout/stderr after discuss with Adriano.
#                   Checked on 4.0.0.2238
#                
# tracker_id:   CORE-5750
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    --set echo on;

    -- All these must fail:
    select timestamp '2018-01-01 10 20 30' from rdb$database;
    select timestamp '2018-01-01 10,20,30 40' from rdb$database;
    select timestamp '31.05.2017 1:2:3.4567' from rdb$database;
    select timestamp '31/05/2017 2:3:4.5678' from rdb$database;
    ------------------------------------------------------------

    -- Date components separator may be a single one (first and second occurence): dash, slash or dot.
    select date '2018-01-31' from rdb$database;
    select date '2018/01/31' from rdb$database;
    select date '2018.01.31' from rdb$database;
    select date '2018' from rdb$database;
    select date '2018,01,31' from rdb$database;
    select date '2018/01.31' from rdb$database;
    select date '2018 01 31' from rdb$database;

    -- Time components (hours to minutes to seconds) separator may be colon.
    select time '10:29:39' from rdb$database;
    select time '10/29/39' from rdb$database;
    select time '10.29.39' from rdb$database;
    select time '10-29-39' from rdb$database;
    select time '10 29 39' from rdb$database;

    -- Seconds to fractions separator may be dot.
    select time '7:3:1.' from rdb$database;
    select time '7:3:2.1238' from rdb$database;
    select time '7:3:3,1238' from rdb$database;

    -- There could *NOT* be any separator (other than spaces) between date and time.
    select timestamp '2018-01-01T01:02:03.4567' from rdb$database;
    select timestamp '31.05.2017       11:22:33.4455' from rdb$database;
    select timestamp '31.05.2017
    22:33:44.5577' from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    2017-05-31 01:02:03.4567  
    2018-01-31  
    2018-01-31  
    2018-01-31  
    2018-01-31  
    10:29:39.0000 
    07:03:01.0000 
    07:03:02.1238 
    2017-05-31 11:22:33.4455  
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 20 30

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: ,20,30 40

    Statement failed, SQLSTATE = 22018
    conversion error from string "31/05/2017 2:3:4.5678"

    Statement failed, SQLSTATE = 22018
    conversion error from string "2018"

    Statement failed, SQLSTATE = 22018
    conversion error from string "2018,01,31"

    Statement failed, SQLSTATE = 22018
    conversion error from string "2018/01.31"

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: /29/39

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: .39

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: -29-39 - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 29 39

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: ,1238

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: T01:02:03.4567

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 
        22:33:44.5577
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

