#coding:utf-8
#
# id:           bugs.core_1346
# title:        lpad and rpad with two columns not working
# decription:   
# tracker_id:   CORE-1346
# min_versions: []
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select lpad('xxx', 8, '0') one, lpad('yyy', 8, '0') two from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
ONE      TWO
======== ========
00000xxx 00000yyy

"""

@pytest.mark.version('>=2.1.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

