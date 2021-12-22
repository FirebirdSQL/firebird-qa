#coding:utf-8
#
# id:           bugs.core_5408
# title:        Result of boolean expression can not be concatenated with string literal
# decription:   
#                  Checked on WI-T4.0.0.466 - works fine.
#                
# tracker_id:   CORE-5408
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select (true = true)|| 'aaa' as "(true=true) concat 'aaa'" from rdb$database;
    select (true is true)|| 'aaa' as "(true is true) concat 'aaa'" from rdb$database;
    select 'aaa' || (true = true) as "'aaa' concat (true = true)" from rdb$database;
    select 'aaa' || (true is true) as "'aaa' concat (true is true)" from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    (true=true) concat 'aaa'        TRUEaaa
    (true is true) concat 'aaa'     TRUEaaa
    'aaa' concat (true = true)      aaaTRUE
    'aaa' concat (true is true)     aaaTRUE
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

