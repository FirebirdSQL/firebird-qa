#coding:utf-8
#
# id:           bugs.core_0223
# title:        ALTER TABLE altering to VARCHAR
# decription:   
# tracker_id:   CORE-0223
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table test1(x int);
    --create index test1_x on test1(x);

    insert into test1 values(2000000000);
    insert into test1 values(100000000);
    insert into test1 values(50000000);
    commit;

    select * from test1 order by x;
    commit;

    alter table test1 alter x type varchar(5);
    alter table test1 alter x type varchar(9);

    alter table test1 alter x type varchar(11);

    -- Here values must be sorted as TEXT:
    select * from test1 order by x;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               50000000
    X                               100000000
    X                               2000000000

    X                               100000000
    X                               2000000000
    X                               50000000
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE TEST1 failed
    -New size specified for column X must be at least 11 characters.

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE TEST1 failed
    -New size specified for column X must be at least 11 characters.
  """

@pytest.mark.version('>=3.0')
def test_core_0223_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

