#coding:utf-8
#
# id:           bugs.core_4006
# title:        using a result from a procedure in a substring expression leads to server crash
# decription:   
# tracker_id:   CORE-4006
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^ ;
    create or alter procedure p_str_rpos
    returns (
        result integer)
    as
    begin
       result=14;
      suspend;
    end^
    set term ; ^
    commit;

    set list on;
    select substring('somestringwith \\ no meaning' from 1 for result) r
    from p_str_rpos; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    R                               somestringwith
  """

@pytest.mark.version('>=2.1.7')
def test_core_4006_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

