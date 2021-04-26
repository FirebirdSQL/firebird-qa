#coding:utf-8
#
# id:           bugs.core_0070
# title:        Expression index regression since 2.0a3
# decription:   
# tracker_id:   CORE-0070
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
    recreate table t1 (col1 varchar(36));
    commit;
    insert into t1 select lower(uuid_to_char(gen_uuid())) from rdb$types rows 100;
    commit;
    create index idx1 on t1 computed by (upper(col1));
    commit;

    set planonly;
    select * from t1 where upper(col1) = '1';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T1 INDEX (IDX1))
  """

@pytest.mark.version('>=2.5')
def test_core_0070_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

