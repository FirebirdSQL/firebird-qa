#coding:utf-8
#
# id:           bugs.core_3972
# title:        Allow the selection of SQL_INT64, SQL_DATE and SQL_TIME in dialect 1
# decription:   
# tracker_id:   CORE-3972
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """
    recreate table t1 (n1 numeric(12,3));
    commit;
    insert into t1 values (1.23);
    insert into t1 values (10.23);
    insert into t1 values (3.567);
    commit;
    set list on;
    select mon$sql_dialect from mon$database;
    select n1, n1 / 2 from t1; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MON$SQL_DIALECT                 1
    N1                              1.230
    DIVIDE                          0.6150000000000000
    N1                              10.230
    DIVIDE                          5.115000000000000
    N1                              3.567
    DIVIDE                          1.783500000000000
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

