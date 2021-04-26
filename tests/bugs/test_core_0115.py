#coding:utf-8
#
# id:           bugs.core_0115
# title:        bug with ALL keyword
# decription:   
# tracker_id:   CORE-0115
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
    recreate table test (i int not null);

    insert into test values (2);
    insert into test values (3);
    commit;

    set plan on;

    set count on;
    select * from test where 1 > all(select i from test);

    commit;

    alter table test add constraint test_pk primary key(i) using index test_pk;
    commit;

    select * from test where i > all(select i from test);
    select * from test where i > 0 and i > all(select i from test where i > 0);

    set count off;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    Records affected: 0

    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    Records affected: 0

    PLAN (TEST INDEX (TEST_PK))
    PLAN (TEST INDEX (TEST_PK))
    Records affected: 0
  """

@pytest.mark.version('>=2.5')
def test_core_0115_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

