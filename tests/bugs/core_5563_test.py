#coding:utf-8
#
# id:           bugs.core_5563
# title:        Use exception instead bugcheck for EVL_expr
# decription:   
#                  Checked on:
#                     fb30Cs, build 3.0.4.32972: OK, 0.687s.
#                     FB30SS, build 3.0.4.32988: OK, 0.672s.
#                     FB40CS, build 4.0.0.955: OK, 1.656s.
#                     FB40SS, build 4.0.0.1008: OK, 0.891s.
#               
#                  NOTE. 
#                  Ability to use nested aggregate looks strange.
#                  Query like here can not be run in MS SQL or Postgress.
#                  Sent letters to dimitr, 19.06.2018.
#                
# tracker_id:   CORE-5563
# min_versions: ['3.0.0']
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
    select
        sum(
            sum(
                (select sum(rf.rdb$field_position) from rdb$relation_fields rf)
               )
           )
    from
        rdb$database
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SUM                             <null>
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

