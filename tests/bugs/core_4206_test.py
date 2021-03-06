#coding:utf-8
#
# id:           bugs.core_4206
# title:        Add RESTART [WITH] clause for alter identity columns
# decription:   
#                   ::: NB :::
#                   Behaviour of FB 4.x was changed since 06-aug-2020 when core-6084 was fixed:
#                   now FB 4.x will assign to ID column values which less than FB 3.x for 1.
#                   For this reason it was changed avoid check for concrete values.
#                   Rather, it is enough to verify only difference between max and min ID.
#               
#                   Checked on 4.0.0.2164, 3.0.7.33356.
#                 
# tracker_id:   CORE-4206
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', ''), ('[\t ]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(
        id int generated by default as identity
       ,x int
    );
    commit;
    insert into test(x) values(1);
    insert into test(x) values(1);
    insert into test(x) values(1);
    commit;

    alter table test alter id restart with 40;
    commit;
    
    insert into test(x) values(2);
    insert into test(x) values(2);
    insert into test(x) values(2);
    commit;

    set list on;
    select x,max(id)-min(id) as id_diff
    from test
    group by x
    order by x;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
     X                               1
     ID_DIFF                         2

     X                               2
     ID_DIFF                         2
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

