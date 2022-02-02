#coding:utf-8

"""
ID:          issue-1444
ISSUE:       1444
TITLE:       ad plan in outer joins with IS NULL clauses (dependent on order of predicates)
DESCRIPTION:
JIRA:        CORE-1029
FBTEST:      bugs.core_1029
"""

import pytest
from firebird.qa import *

init_script = """create table tb1 (id int, col int) ;
create index tbi1 on tb1 (id) ;
create index tbi2 on tb1 (col) ;

insert into tb1 values (1, 1) ;
insert into tb1 values (2, 2) ;
insert into tb1 values (1, null) ;

commit;
"""

db = db_factory(init=init_script)

test_script = """set plan on;

select * from tb1 a
  left join tb1 b on a.id = b.id
  where a.col is null and a.col+0 is null;

select * from tb1 a
  left join tb1 b on a.id = b.id
  where a.col+0 is null and a.col is null;
"""

act = isql_act('db', test_script)

expected_stdout = """PLAN JOIN (A INDEX (TBI2), B INDEX (TBI1))

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

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

