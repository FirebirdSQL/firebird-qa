#coding:utf-8
#
# id:           bugs.core_1401
# title:        Global temporary table instance may pick up not all indices
# decription:   
# tracker_id:   CORE-1401
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1401

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create global temporary table t (f1 int, f2 int, f3 int);
create index idx1 on t (f1);
create index idx2 on t (f2);
create index idx3 on t (f3);
drop index idx2;

set plan on;
insert into t values (1, 1, 1);
select * from t where f1 = 1;
select * from t where f2 = 1;
select * from t where f3 = 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN (T INDEX (IDX1))

          F1           F2           F3
============ ============ ============
           1            1            1


PLAN (T NATURAL)

          F1           F2           F3
============ ============ ============
           1            1            1


PLAN (T INDEX (IDX3))

          F1           F2           F3
============ ============ ============
           1            1            1

"""

@pytest.mark.version('>=2.1')
def test_core_1401_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

