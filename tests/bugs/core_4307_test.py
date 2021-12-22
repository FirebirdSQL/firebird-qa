#coding:utf-8
#
# id:           bugs.core_4307
# title:        Fields present only in WHERE clause of views WITH CHECK OPTION causes invalid CHECK CONSTRAINT violation
# decription:   
# tracker_id:   CORE-4307
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t1 (n1 integer, n2 integer);
    insert into t1 values (1, 2);
    insert into t1 values (1, 3);
    insert into t1 values (1, 4);
    insert into t1 values (2, 2);
    insert into t1 values (2, 3);
    insert into t1 values (2, 4);
    insert into t1 values (3, 2);
    insert into t1 values (3, 3);
    insert into t1 values (3, 4);
    commit;
    recreate view v1 as select n1 from t1 where n1 < n2 with check option;
    commit;
    update v1 set n1 = n1 - 1;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    update v1 set n1 = n1 - 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

