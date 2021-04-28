#coding:utf-8
#
# id:           bugs.core_5913
# title:        Add context variables with compression and encryption status of current connection
# decription:   
#                   Checked on:
#                       3.0.4.33053: OK, 6.375s.
#                       4.0.0.1210: OK, 3.125s.
#                
# tracker_id:   CORE-5913
# min_versions: ['3.0']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select 
         iif( rdb$get_context('SYSTEM','WIRE_COMPRESSED') is not null, 'DEFINED', '<NULL>') as ctx_wire_compressed
        ,iif( rdb$get_context('SYSTEM','WIRE_ENCRYPTED') is not null, 'DEFINED', '<NULL>') as ctx_wire_encrypted
    from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CTX_WIRE_COMPRESSED             DEFINED
    CTX_WIRE_ENCRYPTED              DEFINED
  """

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

