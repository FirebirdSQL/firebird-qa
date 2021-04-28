#coding:utf-8
#
# id:           bugs.core_2339
# title:        Incorrect result for the derived expression based on aggregate and computation
# decription:   
# tracker_id:   CORE-2339
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select * from (select sum(1)*1 as x from rdb$database);
-- result is NULL instead of 1"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                    X
=====================
                    1

"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

