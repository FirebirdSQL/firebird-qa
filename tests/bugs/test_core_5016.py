#coding:utf-8
#
# id:           bugs.core_5016
# title:        Server crashes during GC when DELETE is executed after adding new referencing column
# decription:   
# tracker_id:   CORE-5016
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table a (x integer primary key);
    create table b (x integer primary key);
    insert into b values (1);
    commit;
    alter table b add y integer references a(x);
    commit;
    delete from b;
    commit;
    set list on;
    select count(*) as k from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    K                               1
  """

@pytest.mark.version('>=2.5')
def test_core_5016_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

