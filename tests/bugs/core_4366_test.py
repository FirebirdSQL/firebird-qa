#coding:utf-8
#
# id:           bugs.core_4366
# title:        Wrong result of WHERE predicate when it contains NULL IS NOT DISTINCT FROM (select min(NULL) from ...)
# decription:   
# tracker_id:   CORE-4366
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
recreate table tf(id int primary key, nm varchar(3)); commit;
insert into tf values(5, 'qwe');
insert into tf values(1, 'rty');
insert into tf values(2, 'asd');
insert into tf values(4, 'fgh');
insert into tf values(3, 'mnb');
insert into tf values(7, 'bvc');
insert into tf values(9, 'zxc');
insert into tf values(0, 'lkj');
insert into tf values(6, 'oiu');
insert into tf values(8, 'fgh');
commit;
  """

db_1 = db_factory(page_size=4096, charset='NONE', sql_dialect=3, init=init_script_1)

test_script_1 = """
select nm from tf where null is not distinct from (select min(null) from tf) order by id rows 10;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
NM
======
lkj
rty
asd
mnb
fgh
qwe
oiu
bvc
fgh
zxc
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

