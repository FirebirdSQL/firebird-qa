#coding:utf-8
#
# id:           bugs.core_2117
# title:        Incorrect ROW_COUNT value with indexed retrieval and subquery
# decription:   
# tracker_id:   CORE-2117
# min_versions: []
# versions:     2.1.2
# qmid:         bugs.core_2117

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.2
# resources: None

substitutions_1 = []

init_script_1 = """create table t (n integer);

insert into t values (1);
insert into t values (2);
insert into t values (3);

commit;

create index t_n on t (n);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set term !!;

execute block returns (n integer)
as
  declare x integer;
begin
  update t set n = n where n = -1;
  n = row_count;
  suspend;

  update t set n = n where n = (select -1 from rdb$database);
  n = row_count;
  suspend;

  update t set n = n where n = -1;
  n = row_count;
  suspend;

  for select 1 from t where n = -1 into x do
  begin
  end
  n = row_count;
  suspend;

  for select 1 from t where n = (select -1 from rdb$database) into x do
  begin
  end
  n = row_count;
  suspend;

  delete from t where n = (select -1 from rdb$database);
  n = row_count;
  suspend;
end!!

set term ;!!"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           N
============
           0
           0
           0
           0
           0
           0

"""

@pytest.mark.version('>=2.1.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

