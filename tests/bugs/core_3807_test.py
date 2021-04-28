#coding:utf-8
#
# id:           bugs.core_3807
# title:        Error "Invalid expression in the select list" can be unexpectedly raised if a string literal is used inside a GROUP BY clause in a multi-byte connection
# decription:   
# tracker_id:   CORE-3807
# min_versions: ['2.1.5']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select
    'Current time is ' || cast(a.t as varchar(15))
from
    (select '16:06:03.0000' t from rdb$database) a
group by
    'Current time is ' || cast(a.t as varchar(15));
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
CONCATENATION
===============================
Current time is 16:06:03.0000

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

