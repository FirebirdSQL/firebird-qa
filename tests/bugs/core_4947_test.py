#coding:utf-8
#
# id:           bugs.core_4947
# title:        Compound ALTER TABLE statement with ADD and DROP the same check constraint fails
# decription:   
# tracker_id:   CORE-4947
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t(x int not null);
    alter table t
        add constraint cx check(x > 0),
        drop constraint cx; 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

