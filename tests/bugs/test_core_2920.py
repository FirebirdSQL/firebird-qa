#coding:utf-8
#
# id:           bugs.core_2920
# title:        Incorrect execution of volatile SQL statements inside EXECUTE STATEMENT
# decription:   
# tracker_id:   CORE-2920
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table bugtest (id int);
insert into bugtest (id) values (123);
set term !!;
create procedure p_bugtest (in_id int)
  returns (cnt int)
as
  declare predicate varchar(1000);
begin
  if (:in_id is null) then
    predicate = ' ? is null';
  else
    predicate = ' id = ?';

  execute statement ('select count(*) from bugtest where' || predicate) (:in_id)
  into :cnt;
end!!
set term !!;
commit;"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """execute procedure p_bugtest (123);
-- cnt = 1
execute procedure p_bugtest (null);
-- cnt = 1
execute procedure p_bugtest (123);
-- cnt = 1
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
         CNT
============
           1


         CNT
============
           1


         CNT
============
           1

"""

@pytest.mark.version('>=2.5.0')
def test_core_2920_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

