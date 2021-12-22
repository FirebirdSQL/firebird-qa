#coding:utf-8
#
# id:           bugs.core_3503
# title:        ALTER VIEW crashes the server if the new version has an artificial (aggregate or union) stream at the position of a regular context in the older version
# decription:   
#                   Checked on:
#                       4.0.0.1635 SS: 1.890s.
#                       3.0.5.33182 SS: 1.207s.
#                       2.5.9.27146 SC: 0.360s.
#                
# tracker_id:   CORE-3503
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(from_backup='core3503.fbk', init=init_script_1)

test_script_1 = """
    create or alter view v_test (id)
    as
    select rdb$relation_id from rdb$relations
    union all
    select rdb$relation_id from rdb$relations;
    commit; -- here the crash happens 
    set list on;
    select (select count(id) from v_test) / count(*) c
    from rdb$relations;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    C                               2
"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

