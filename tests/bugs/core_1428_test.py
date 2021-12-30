#coding:utf-8
#
# id:           bugs.core_1428
# title:        Incorrect timestamp substraction in 3 dialect when result is negative number
# decription:   
#                27.07.2021: changed output form using SET LIST ON, added subst. to remove dependency on the number of inner spaces.
#                Checked on:
#                   5.0.0.113 SS: 1.025s.
#                   5.0.0.88 SS: 1.028s.
#                   4.0.1.2539 SS: 0.942s.
#                   3.0.8.33476 SS: 2.076s.
#                
# tracker_id:   CORE-1428
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1428

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
        select (cast('2007-08-22 00:00:00.0019' as timestamp) - cast('2007-08-22 00:00:00.0000' as timestamp)) *86400*10000 as dts_01 from rdb$database;
        select (cast('2007-08-22 00:00:00.0000' as timestamp) - cast('2007-08-22 00:00:00.0019' as timestamp)) *86400*10000 as dts_02 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
        DTS_01 19.008000000
        DTS_02 -19.008000000  
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

