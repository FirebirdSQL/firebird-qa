#coding:utf-8
#
# id:           bugs.core_4093
# title:        Server crashes while converting an overscaled numeric to a string
# decription:   
# tracker_id:   CORE-4093
# min_versions: ['2.5.0']
# versions:     2.5, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select cast(cast(0 as numeric(18, 15)) * cast(0 as numeric(18, 15)) * cast(0 as numeric(18, 15)) as varchar (41)) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22018
    conversion error from string "0.000000000000000000000000000000000000000000000"
"""

@pytest.mark.version('>=2.5,<4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set heading off;
    select cast( cast(0 as numeric(38, 38)) * cast(0 as numeric(38, 38)) * cast(0 as numeric(38, 38)) as varchar(100) ) from rdb$database;
    select cast( cast(0 as numeric(38, 38)) * cast(0 as numeric(38, 38)) * cast(0 as numeric(38, 38)) as numeric(38, 38) ) from rdb$database;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    0E-114
    0.00000000000000000000000000000000000000
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

