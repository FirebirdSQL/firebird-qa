#coding:utf-8
#
# id:           bugs.core_1078
# title:        View with equally named source fields not faisible
# decription:   
# tracker_id:   CORE-1078
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1078

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """create table t1(id integer, field1 integer);
create table t2(id integer, field1 integer);
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create view view1 as select t1.field1 as t1f1, t2.field1 as t2f1 from t1 JOIN t2 on t2.id = t1.id;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.execute()

