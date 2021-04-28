#coding:utf-8
#
# id:           bugs.core_2397
# title:        If you drop two different indexes within the same transaction, you get database corruption
# decription:   
# tracker_id:   CORE-2397
# min_versions: []
# versions:     2.1.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.3
# resources: None

substitutions_1 = []

init_script_1 = """create table test(id int, title varchar(50));
commit;
create index test1 on test computed by (id +1);
create index test2 on test computed by (id +2);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET AUTODDL OFF;
drop index test1;
drop index test2;
commit;
insert into test values(1,'test');
commit;
SELECT id from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID
============
           1

"""

@pytest.mark.version('>=2.1.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

