#coding:utf-8
#
# id:           bugs.core_3523
# title:        SIMILAR TO: False matches on descending ranges
# decription:   
# tracker_id:   CORE-3523
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

test_script_1 = """select 1 from rdb$database where 'm' similar to '[p-k]'
union
select 2 from rdb$database where 'z' similar to '[p-k]'
union
select 3 from rdb$database where 'm' not similar to '[p-k]'
union
select 4 from rdb$database where 'z' not similar to '[p-k]';

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """SQL>
    CONSTANT
============
           3
           4

SQL>"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

