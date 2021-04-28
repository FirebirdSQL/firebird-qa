#coding:utf-8
#
# id:           bugs.core_5846
# title:        CREATE VIEW issues "Implementation of text subtype 512 not located"
# decription:   
#                   Works fine on:
#                       3.0.4.32995: OK, 1.047s.
#                       4.0.0.1028: OK, 1.391s.
#                
# tracker_id:   CORE-5846
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    alter character set utf8 set default collation unicode;
    create table table1( fld1 char(1) character set none );

    -- NB: 'expected_stderr' must remain empty as result of following command.
    create view view1 as
    select fld1 from table1
    ; 
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.execute()

