#coding:utf-8
#
# id:           bugs.core_1650
# title:        Infinite row generation in "select gen_id(..) from rdb$database" with "group by"
# decription:   
# tracker_id:   CORE-1650
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create generator g;
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select first 10 1, gen_id(g, 1 )
from rdb$database
group by 1,2;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CONSTANT                GEN_ID
============ =====================
           1                     3

"""

@pytest.mark.version('>=2.5.0')
def test_core_1650_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

