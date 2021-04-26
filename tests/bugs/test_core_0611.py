#coding:utf-8
#
# id:           bugs.core_0611
# title:        SKIP is off by one
# decription:   
# tracker_id:   CORE-0611
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table A (id integer not null);
    commit;
    insert into A (id) values (1);
    insert into A (id) values (2);
    insert into A (id) values (3);
    commit;
    set list on;
    select skip 0 id from a order by id;
    select skip 2 id from a order by id;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    ID                              2
    ID                              3
    ID                              3
  """

@pytest.mark.version('>=2.1.7')
def test_core_0611_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

