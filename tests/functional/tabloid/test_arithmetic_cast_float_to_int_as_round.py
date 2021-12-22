#coding:utf-8
#
# id:           functional.tabloid.arithmetic_cast_float_to_int_as_round
# title:        Result of CAST for numbers is implementation defined
# decription:   See also: sql.ru/forum/actualutils.aspx?action=gotomsg&tid=1062610&msg=15214333
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on; select cast( sqrt(24) as smallint) casted_sqrt from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CASTED_SQRT                     5
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

