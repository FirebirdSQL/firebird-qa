#coding:utf-8
#
# id:           bugs.core_1274
# title:        Wrong results when PLAN MERGE is chosen and datatypes of the equality predicate arguments are different
# decription:   
# tracker_id:   CORE-1274
# min_versions: ['2.1.4']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (col1 int);
create table t2 (col2 varchar(10));
commit;

insert into t1 values (100);
insert into t1 values (20);
insert into t1 values (3);
commit;

insert into t2 values ('100');
insert into t2 values ('20');
insert into t2 values ('3');
commit;"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select * from t1 join t2 on col1 = col2 ORDER by 1 DESC;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
        COL1 COL2
============ ==========
         100 100
          20 20
           3 3

"""

@pytest.mark.version('>=3.0')
def test_core_1274_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

