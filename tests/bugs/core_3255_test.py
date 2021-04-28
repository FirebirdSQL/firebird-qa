#coding:utf-8
#
# id:           bugs.core_3255
# title:        The server could crash using views with GROUP BY
# decription:   
# tracker_id:   CORE-3255
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM !;
create table t1 (
  n1 integer
)!

create view v1 (x, n1) as
  select 'a', n1
    from t1
group by 1, n1!

insert into t1 values (1)!
insert into t1 values (1)!
insert into t1 values (2)!
insert into t1 values (2)!
insert into t1 values (3)!

commit!

create or alter procedure p1 returns (x varchar(1), n1 integer)
as
begin
  for select x, n1 from v1 into x, n1 do
      suspend;
end!

create or alter procedure p2 returns (x varchar(1), n1 integer)
as
begin
  for select n1 from t1 into n1 do
  begin
  end

  for select n1, x from v1 into n1, x do
      suspend;
end!

commit!
SET TERM ;!
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select * from p2;
select * from p1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_3255.fdb, User: SYSDBA
SQL>
X                N1
====== ============
a                 1
a                 2
a                 3

SQL>
X                N1
====== ============
a                 1
a                 2
a                 3

SQL>"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

