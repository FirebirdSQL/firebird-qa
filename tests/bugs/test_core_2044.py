#coding:utf-8
#
# id:           bugs.core_2044
# title:        Incorrect result with UPDATE OR INSERT ... RETURNING OLD and non-nullable columns
# decription:   
# tracker_id:   CORE-2044
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t (
    n integer primary key,
    x1 integer not null,
    x2 integer
);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """update or insert into t
    values (1, 1, 1)
    returning old.n, old.x1, old.x2, new.n, new.x1, new.x2;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CONSTANT     CONSTANT     CONSTANT            N           X1           X2
============ ============ ============ ============ ============ ============
      <null>       <null>       <null>            1            1            1

"""

@pytest.mark.version('>=2.5.0')
def test_core_2044_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

