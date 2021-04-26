#coding:utf-8
#
# id:           bugs.core_1120
# title:        Conversion from string to number is not standard compliant
# decription:   
# tracker_id:   CORE-1120
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_1120-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select cast(5.6 as integer) from rdb$database;
select cast('5.6' as integer) from rdb$database;
select cast('5,6' as integer) from rdb$database;
select cast('5,6,7 8 9' as integer) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """CAST
============
           6

CAST
============
           6

CAST
============
CAST
============
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 22018
conversion error from string "5,6"
Statement failed, SQLSTATE = 22018
conversion error from string "5,6,7 8 9"
"""

@pytest.mark.version('>=2.5.0')
def test_core_1120_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

