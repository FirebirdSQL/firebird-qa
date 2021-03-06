#coding:utf-8
#
# id:           functional.intfunc.date.dateadd_08
# title:        Dateadd milliseconds
# decription:   
# tracker_id:   CORE-1387
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.date.dateadd_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select dateadd(-1 millisecond to time '12:12:00:0000' ) as test from rdb$database;
select dateadd(millisecond,-1, time '12:12:00:0000' ) as test from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
         TEST
=============
12:11:59.9990


         TEST
=============
12:11:59.9990

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

