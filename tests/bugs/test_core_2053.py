#coding:utf-8
#
# id:           bugs.core_2053
# title:        Computed expressions may be optimized badly if used inside the RETURNING clause of the INSERT statement
# decription:   
# tracker_id:   CORE-2053
# min_versions: []
# versions:     2.1.2
# qmid:         bugs.core_2053

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.2
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (col1 int);
create index i1 on t1 (col1);
commit;
insert into t1 (col1) values (1);
commit;
create table t2 (col2 int);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
insert into t2 (col2) values (1) returning case when exists (select 1 from t1 where col1 = col2) then 1 else 0 end;
commit;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN (T1 INDEX (I1))

        CASE
============
           1

"""

@pytest.mark.version('>=2.1.2')
def test_core_2053_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

