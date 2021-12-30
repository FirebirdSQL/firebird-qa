#coding:utf-8
#
# id:           bugs.core_2720
# title:        Wrong evaluation result with divide and unary plus\\minus operations
# decription:   
#                 27.07.2021: changed output form using SET LIST ON, added subst. to remove dependency on the number of inner spaces.
#                 Checked on:
#                   5.0.0.113 SS: 0.976s.
#                   5.0.0.88 SS: 0.959s.
#                   4.0.1.2539 SS: 0.943s.
#                   3.0.8.33476 SS: 1.741s.
#                   2.5.9.27152 SC: 0.278s.
#                 
# tracker_id:   CORE-2720
# min_versions: ['2.0.6']
# versions:     2.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.6
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select
        36/4/3    div_01
       ,36/-4/3   div_02
       ,36/+4/3   div_03
       ,36/+-4/3  div_04
       ,36/-+4/3  div_05
       ,36/- -4/3 div_06
       ,36/++4/3  div_07
       ,- -36/- -4/- -3 div_08
       ,- -36/- -3/- -4 div_09
       ,- +36/+ -3/+ -4 div_10
    from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DIV_01 3
    DIV_02 -3
    DIV_03 3
    DIV_04 -3
    DIV_05 -3
    DIV_06 3
    DIV_07 3
    DIV_08 3
    DIV_09 3
    DIV_10 -3
"""

@pytest.mark.version('>=2.0.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

