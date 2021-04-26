#coding:utf-8
#
# id:           bugs.core_0610
# title:        FIRST is applied before aggregation
# decription:   
# tracker_id:   CORE-0610
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
    create table B (id integer not null, A integer not null, v integer);
    commit;
    insert into A (id) values (1);
    insert into A (id) values (2);
    insert into A (id) values (3);
    insert into B (id, A, v) values (1, 1, 1);
    insert into B (id, A, v) values (2, 1, 1);
    insert into B (id, A, v) values (3, 2, 2);
    insert into B (id, A, v) values (4, 2, 2);
    insert into B (id, A, v) values (5, 3, 3);
    insert into B (id, A, v) values (6, 3, 3);
    commit;
    set list on;
    select first 1 count(*) from a;
    select first 2 a.id, sum(b.v) from A,B where a.id = b.a
    group by a.id
    order by a.id;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COUNT                           3
    ID                              1
    SUM                             2
    ID                              2
    SUM                             4
  """

@pytest.mark.version('>=2.1.7')
def test_core_0610_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

