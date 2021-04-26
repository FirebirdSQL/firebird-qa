#coding:utf-8
#
# id:           bugs.core_4073
# title:        Constant columns getting empty value with subselect from procedure
# decription:   
# tracker_id:   CORE-4073
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """
    create domain d_vc10 varchar(10);
    commit;
    set term ^;
    create or alter procedure P_TEST returns (TEXT D_VC10) as
    begin
      TEXT = '12345'; suspend;
    end^
    set term ;^
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select A, TEXT from (select '2' as A, TEXT from P_TEST);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               2
    TEXT                            12345
  """

@pytest.mark.version('>=2.1.7')
def test_core_4073_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

