#coding:utf-8
#
# id:           bugs.core_4227
# title:        Regression: Wrong evaluation of BETWEEN and boolean expressions due to parser conflict
# decription:   
# tracker_id:   CORE-4227
# min_versions: ['2.0']
# versions:     2.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select 1 x from rdb$database where rdb$relation_id between 1 and 500 and rdb$description is null;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               1
"""

@pytest.mark.version('>=2.0.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

