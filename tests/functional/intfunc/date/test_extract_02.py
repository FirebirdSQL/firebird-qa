#coding:utf-8
#
# id:           functional.intfunc.date.extract_02
# title:        test extract function with miliseconds
# decription:   
# tracker_id:   CORE-1387
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.date.extract_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select extract(millisecond from time '12:12:00.1111' ) as test from rdb$database;
select extract(millisecond from timestamp '2008-12-08 12:12:00.1111' ) as test from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
        TEST
============
       111.1


        TEST
============
       111.1

"""

@pytest.mark.version('>=2.1')
def test_extract_02_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

