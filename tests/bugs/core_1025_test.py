#coding:utf-8
#
# id:           bugs.core_1025
# title:        Server crashes at runtime when an explicit MERGE plan is specified over a few JOIN ones
# decription:   
# tracker_id:   CORE-1025
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_1025

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """recreate table t (id int not null);
alter table t add constraint pk primary key (id);

insert into t values (1);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select *
from t t1, t t2, t t3, t t4
where t1.id = t2.id
  and t2.id = t3.id
  and t3.id = t4.id
PLAN MERGE (JOIN (T1 NATURAL, T2 INDEX (PK)), JOIN(T3 NATURAL, T4 INDEX (PK)));

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID           ID           ID           ID
============ ============ ============ ============
           1            1            1            1

"""

@pytest.mark.version('>=2.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

