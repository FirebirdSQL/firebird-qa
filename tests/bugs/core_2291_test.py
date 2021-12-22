#coding:utf-8
#
# id:           bugs.core_2291
# title:        BUGCHECK 284 (cannot restore singleton select data (284), file: rse.cpp ...)
# decription:   
# tracker_id:   CORE-2291
# min_versions: ['2.0.6']
# versions:     2.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.6
# resources: None

substitutions_1 = []

init_script_1 = """recreate table t (id int, f2 char(16));
commit;

insert into t values (1, '0123456798012345');
insert into t values (2, '0123456798012345');
commit;

alter table t drop f2;
commit;

update t set id = 3 where id = 2;
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM !!;
execute block returns (id int)
as
begin
  select t1.id from t t1 left join t t2 on t1.id = t2.id - 2
   where t2.id = 3
    into :id;
  suspend;
end !!
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID
============
           1

"""

@pytest.mark.version('>=2.0.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

