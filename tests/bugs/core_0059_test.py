#coding:utf-8
#
# id:           bugs.core_0059
# title:        Automatic not null in PK columns incomplete
# decription:   
# tracker_id:   CORE-0059
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
    recreate table test (a int, b float, c varchar(10), primary key (a, b, c));
    commit;
    insert into test(a) values(null);
    insert into test(a,b) values(1,null);
    insert into test(a,b,c) values(1,1,null);
    insert into test default values;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."A", value "*** null ***"
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."B", value "*** null ***"
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."C", value "*** null ***"
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."A", value "*** null ***"
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

