#coding:utf-8
#
# id:           bugs.core_1690
# title:        arithmetic exception, numeric overflow, or string truncation in utf8 tables
# decription:   
# tracker_id:   CORE-1690
# min_versions: []
# versions:     2.1.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.3
# resources: None

substitutions_1 = []

init_script_1 = """create table A (C1 INTEGER PRIMARY KEY);
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """show table A;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """C1                              INTEGER Not Null
CONSTRAINT INTEG_2:
  Primary key (C1)
"""

@pytest.mark.version('>=2.1.3')
def test_core_1690_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

