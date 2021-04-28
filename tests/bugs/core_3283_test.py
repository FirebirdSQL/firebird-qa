#coding:utf-8
#
# id:           bugs.core_3283
# title:        BAD PLAN with using LEFT OUTER JOIN in SUBSELECT
# decription:   
# tracker_id:   CORE-3283
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table ttt (
        id int
        ,constraint ttt_pk primary key (id) using index ttt_id
    );
    
    insert into ttt (id) values (0);
    insert into ttt (id) values (1);
    insert into ttt (id) values (2);
    insert into ttt (id) values (3);
    insert into ttt (id) values (4);
    insert into ttt (id) values (5);
    commit;
    
    set planonly;
    select t1.id from ttt t1
    where t1.id =
    (select t3.id 
       from ttt t2
       left join ttt t3 on t3.id > t2.id
      where t2.id = 3 
      order by t3.id
       rows 1
    );

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (JOIN (T2 INDEX (TTT_ID), T3 INDEX (TTT_ID)))
    PLAN (T1 INDEX (TTT_ID))
  """

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

