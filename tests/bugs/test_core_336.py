#coding:utf-8
#
# id:           bugs.core_336
# title:        DateTime math imprecision
# decription:   
# tracker_id:   CORE-336
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_336-21

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select (cast('01.01.2004 10:01:00' as timestamp)-cast('01.01.2004 10:00:00' as timestamp))+cast('01.01.2004 10:00:00' as timestamp) from rdb$database ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ADD
=========================
2004-01-01 10:01:00.0000

"""

@pytest.mark.version('>=2.1')
def test_core_336_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

