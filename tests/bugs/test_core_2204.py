#coding:utf-8
#
# id:           bugs.core_2204
# title:        constraints on sp output parameters are checked even when the sp returns zero rows
# decription:   
# tracker_id:   CORE-2204
# min_versions: ['3.0']
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
    create domain dm_boo as integer not null check (value = 0 or value = 1);
    set term ^;
    create procedure test returns (b dm_boo) as
    begin
        if (1 = 0) then
            suspend;
    end
    ^
    set term ;^
    commit;
    set count on;
    select * from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """

@pytest.mark.version('>=3.0')
def test_core_2204_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

