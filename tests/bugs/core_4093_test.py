#coding:utf-8
#
# id:           bugs.core_4093
# title:        Server crashes while converting an overscaled numeric to a string
# decription:   
# tracker_id:   CORE-4093
# min_versions: ['2.5.0']
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
    select cast( cast(0 as numeric(38, 38)) * cast(0 as numeric(38, 38)) * cast(0 as numeric(38, 38)) as varchar(100) ) from rdb$database;
    select cast( cast(0 as numeric(38, 38)) * cast(0 as numeric(38, 38)) * cast(0 as numeric(38, 38)) as numeric(38, 38) ) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    0E-114
    0.00000000000000000000000000000000000000
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

