#coding:utf-8
#
# id:           bugs.core_2081
# title:        RDB$DB_KEY in subselect expression incorrectly returns NULL
# decription:   
# tracker_id:   CORE-2081
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select a.rdb$db_key, (select b.rdb$db_key from rdb$database b)
  from rdb$database a;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
DB_KEY           DB_KEY
================ ================
0100000001000000 0100000001000000

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

