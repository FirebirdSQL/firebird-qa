#coding:utf-8
#
# id:           bugs.core_0896
# title:        SUBSTRING with NULL offset or length don't return NULL
# decription:   
# tracker_id:   CORE-896
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_896

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select substring('abc' from null) from rdb$database;
select substring('abc' from 2 for null) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """SUBSTRING
=========
<null>

SUBSTRING
=========
<null>

"""

@pytest.mark.version('>=2.1')
def test_core_0896_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

