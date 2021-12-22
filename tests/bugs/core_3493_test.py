#coding:utf-8
#
# id:           bugs.core_3493
# title:        Adding a value to a timestamp below '16.11.1858 00:00:01' throws 'value exceeds the range for valid timestamp'
# decription:   
# tracker_id:   CORE-3493
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT CAST('01.01.0200 12:00:00' as timestamp) + 1 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """SQL>
                      ADD
=========================
0200-01-02 12:00:00.0000
"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

