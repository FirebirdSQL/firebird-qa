#coding:utf-8
#
# id:           functional.tabloid.arithmetic_numexpr_eval_dialect_3
# title:        Check result of integer division on dialect 3.
# decription:   Was fixed in 2.1, see: sql.ru/forum/actualutils.aspx?action=gotomsg&tid=708324&msg=7865013
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on; select 36/-4/3 d from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    D                               -3
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

