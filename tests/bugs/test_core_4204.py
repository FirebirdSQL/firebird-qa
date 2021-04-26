#coding:utf-8
#
# id:           bugs.core_4204
# title:         Error when compiling the procedure containing the statement if (x = (select ...))
# decription:   
# tracker_id:   CORE-4204
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create or alter procedure Test_C
    as
      declare variable X varchar(16);
    begin
    
      if (x = (select '123' from Rdb$Database)) then
      begin
        exit;
      end
    end 
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.3')
def test_core_4204_1(act_1: Action):
    act_1.execute()

