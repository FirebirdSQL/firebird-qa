#coding:utf-8
#
# id:           full_join_push_where_predicate
# title:        WHERE-filter must be applied after FULL JOIN result
# decription:   
#                   See (rus): https://www.sql.ru/forum/1326682/dva-cte-ih-full-join-i-uslovie-daut-nekorrektnyy-rezultat
#                   Confirmed bug on 2.5.9.27151.
#                   Checked on 3.0.6.33322, 4.0.0.2073 -- all fine.
#                 
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    recreate table t (
        f1  varchar(10),
        f2  integer
    );

    insert into t (f1, f2) values ('a', 1);
    insert into t (f1, f2) values ('b', 1);
    insert into t (f1, f2) values ('c', 1);
    insert into t (f1, f2) values ('b', 2);
    insert into t (f1, f2) values ('c', 2);
    insert into t (f1, f2) values ('d', 2);
    commit;

    with
      t1 as (select f1 from t where f2 = 1)
     ,t2 as (select f1 from t where f2 = 2)
    select
      t1.f1 t1_f1,
      t2.f1 t2_f1
    from
      t1 full join t2 on t1.f1 = t2.f1
    where t1.f1 is null
    order by 1,2
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    T1_F1                           <null>
    T2_F1                           d
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

