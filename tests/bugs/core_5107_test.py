#coding:utf-8
#
# id:           bugs.core_5107
# title:        set autoddl off and sequence of: ( create view V as select * from T; alter view V as select 1 x from rdb$database; drop view V; ) leads to server crash
# decription:   
#                 
# tracker_id:   CORE-5107
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set autoddl off;
    commit;
    recreate table test(id int, x int);
    create view v_test as select * from test;
    alter view v_test as select 1 id from rdb$database;
    drop view v_test;
    commit;
    set list on;
    select 'Done' as msg from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             Done
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

