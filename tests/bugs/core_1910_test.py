#coding:utf-8
#
# id:           bugs.core_1910
# title:        Not valid fields in MERGE's insert clause are allowed
# decription:   
# tracker_id:   CORE-1910
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('column.*', '')]

init_script_1 = """create table t1 (n integer, x integer);
create table t2 (a integer, b integer);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """merge into t1 t1
  using (select * from t2) t2
    on t1.n = t2.a
    when matched then
      update set x = t2.b
    when not matched then
      insert (a, x) values (1, 2); -- "a" is not a field of t1
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42S22
Dynamic SQL Error
-SQL error code = -206
-Column unknown
-A
-At line 7, column 15
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

