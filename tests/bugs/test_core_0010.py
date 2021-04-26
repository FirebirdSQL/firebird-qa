#coding:utf-8
#
# id:           bugs.core_0010
# title:        Navigation vs IS NULL vs compound index
# decription:   
# tracker_id:   CORE-0010
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
    recreate table t (f1 int, f2 int);
    create index t_idx on t (f1, f2);

    insert into t (f1, f2) values (1, 1);
    insert into t (f1, f2) values (null, 2);
    insert into t (f1, f2) values (3, 3);

    set list on;

    select *
    from t
    where f1 is null
    order by f1, f2;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F1                              <null>
    F2                              2
  """

@pytest.mark.version('>=2.5')
def test_core_0010_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

