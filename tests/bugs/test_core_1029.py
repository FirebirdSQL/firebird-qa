#coding:utf-8
#
# id:           bugs.core_1029
# title:        Bad plan in outer joins with IS NULL clauses (dependent on order of predicates)
# decription:   
# tracker_id:   CORE-1029
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_1029

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """create table tb1 (id int, col int) ;
create index tbi1 on tb1 (id) ;
create index tbi2 on tb1 (col) ;

insert into tb1 values (1, 1) ;
insert into tb1 values (2, 2) ;
insert into tb1 values (1, null) ;

commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set plan on;

select * from tb1 a
  left join tb1 b on a.id = b.id
  where a.col is null and a.col+0 is null;

select * from tb1 a
  left join tb1 b on a.id = b.id
  where a.col+0 is null and a.col is null;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN JOIN (A INDEX (TBI2), B INDEX (TBI1))

          ID          COL           ID          COL
============ ============ ============ ============
           1       <null>            1            1
           1       <null>            1       <null>

PLAN JOIN (A INDEX (TBI2), B INDEX (TBI1))

          ID          COL           ID          COL
============ ============ ============ ============
           1       <null>            1            1
           1       <null>            1       <null>

"""

@pytest.mark.version('>=2.0.1')
def test_core_1029_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

