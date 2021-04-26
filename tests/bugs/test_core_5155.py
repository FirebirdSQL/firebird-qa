#coding:utf-8
#
# id:           bugs.core_5155
# title:        [CREATE OR] ALTER USER statement: clause PASSWORD (if present) must be always specified just after USER
# decription:   
# tracker_id:   CORE-5155
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
    create or alter user tmp$c5155 password '123' firstname 'john' revoke admin role; 
    create or alter user tmp$c5155 revoke admin role firstname 'john' password '123'; 
    create or alter user tmp$c5155 firstname 'john' revoke admin role password '123' lastname 'smith'; 
    create or alter user tmp$c5155 lastname 'adams' grant admin role firstname 'mick' password '123'; 
    create or alter user tmp$c5155 revoke admin role lastname 'adams' firstname 'mick' password '123'; 
    drop user tmp$c5155;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_5155_1(act_1: Action):
    act_1.execute()

