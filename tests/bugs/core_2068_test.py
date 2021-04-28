#coding:utf-8
#
# id:           bugs.core_2068
# title:        Comparision with IN and subquery with RDB$DB_KEY returns wrong result
# decription:   
# tracker_id:   CORE-2068
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (n integer);

insert into t1 values (1);
insert into t1 values (2);
insert into t1 values (3);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select a.*
 from t1 a
 where a.rdb$db_key = (
 select b.rdb$db_key
 from t1 b
 where n = 1
);

select a.*
 from t1 a
 where a.rdb$db_key in (
 select b.rdb$db_key
 from t1 b
 where n = 1
);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           N
============
           1


           N
============
           1

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

