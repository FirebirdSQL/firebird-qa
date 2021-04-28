#coding:utf-8
#
# id:           bugs.core_2051
# title:        don't work subquery in COALESCE
# decription:   
# tracker_id:   CORE-2051
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         bugs.core_2051

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ 
    recreate table test1(id int primary key using index test1_pk);
    commit;
    insert into test1 values(1);
    insert into test1 values(2);
    insert into test1 values(3);
    commit;
    
    recreate table test2(id int primary key using index test2_pk);
    commit;
    insert into test2 values(1);
    insert into test2 values(2);
    commit;
    
    set plan on;
    set list on;
    select coalesce((select t2.id from test2 t2 where t2.id = t1.id), 0) id2 from test1 t1 order by t1.id;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T2 INDEX (TEST2_PK))
    PLAN (T1 ORDER TEST1_PK)
    ID2                             1
    ID2                             2
    ID2                             0
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

