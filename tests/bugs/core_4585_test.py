#coding:utf-8
#
# id:           bugs.core_4585
# title:        Can't create column check constraint when the column is domain based
# decription:   
# tracker_id:   CORE-4585
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain x int;
    create table test(
        x x constraint test_x_chk check(x>0)
    );
    insert into test(x) values(1);
    insert into test(x) values(0);
    set list on;
    select * from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    Operation violates CHECK constraint TEST_X_CHK on view or table TEST
    -At trigger 'CHECK_1'
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

