#coding:utf-8
#
# id:           bugs.core_3553
# title:        Nested loop plan is chosen instead of the sort merge for joining independent streams using keys of different types
# decription:   
# tracker_id:   CORE-3553
# min_versions: ['2.1.5']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
select count(*)
from rdb$database d1 join rdb$database d2
  on cast(d1.rdb$relation_id as char(10)) = cast(d2.rdb$relation_id as char(20));
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN HASH (D2 NATURAL, D1 NATURAL)

                COUNT
=====================
                    1

"""

@pytest.mark.version('>=3.0')
def test_core_3553_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

