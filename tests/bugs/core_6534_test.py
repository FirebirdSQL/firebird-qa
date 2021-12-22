#coding:utf-8
#
# id:           bugs.core_6534
# title:        Hash join cannot match records using some TIME ZONE / DECFLOAT keys
# decription:   
#                   Confirmed bug on 4.0.0.2387.
#                   Checked on intermediate build 4.0.0.2406 (built 06-apr-2021 12:40) - all OK.
#                 
# tracker_id:   CORE-6534
# min_versions: ['4.0']
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- All subsequent statements must return non-empty result:
    set heading off;
    select 1 from (select timestamp '01.01.2021 13:00:00 +03:00' as ts from rdb$database) natural join (select timestamp '01.01.2021 12:00:00 +02:00' as ts from rdb$database);
    select 2 from (select cast(10 as decfloat) as df from rdb$database) natural join (select cast(10.000 as decfloat) as df from rdb$database);
    select 3 from (select cast('+0' as decfloat) as df from rdb$database) natural join (select cast('-0' as decfloat) as df from rdb$database);
    select 4 from (select cast('+0' as float) as f from rdb$database) natural join (select cast('-0' as float) as f from rdb$database); 
    select 5 from (select cast('+0' as double precision) as d from rdb$database) natural join (select cast('-0' as double precision) as d from rdb$database);
    select 6 from (select cast('0E-6176' as decfloat) as d from rdb$database) natural join (select cast('0e0' as decfloat) as d from rdb$database);
    select 7 from (select time '05:05:05.5555' at time zone '-10:0' t from rdb$database) natural join (select time '05:05:05.5555' at time zone '+14:0' t from rdb$database);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1
    2
    3
    4
    5
    6
    7
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

