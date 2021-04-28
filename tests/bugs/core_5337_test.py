#coding:utf-8
#
# id:           bugs.core_5337
# title:        Regression: The subquery in the insert list expressions ignore the changes made earlier in the same executable block.
# decription:   
#                  Confirmed  on WI-T4.0.0.372 (nightly build)
#                  Works fine on:
#                  * 4.0.0.372 - after commit 21-sep-2016 12:39
#                    https://github.com/FirebirdSQL/firebird/commit/d8f43da00f10181495160d12f17556fe9cc5687b
#                  *  WI-V3.0.1.32609 -  after commit 25-sep-2016 23:47
#                    https://github.com/FirebirdSQL/firebird/commit/d5ff6d82c2d9edba7b6def2e6a32f753b856227a
#                
# tracker_id:   CORE-5337
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test (
        id integer not null,
        val integer not null
    );

    set term ^;
    execute block
    as
    begin
      insert into test (id, val) values (1, 100);
      insert into test (id, val) values (2, (select val from test where id = 1));
    end
    ^
    set term ;^

    set list on;
    select * from test;
    rollback;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    VAL                             100

    ID                              2
    VAL                             100
  """

@pytest.mark.version('>=3.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

