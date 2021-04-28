#coding:utf-8
#
# id:           bugs.core_6186
# title:        Original content of column which is involved into ENCRYPT() is displayed as distorted view after this call
# decription:   
#                   Confirmed bug on 4.0.0.1637
#                   Checked on 4.0.0.1691: OK, 1.124s.
#                
# tracker_id:   CORE-6186
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    with
    a as (
        select 'Encrypts/decrypts data using symmetric cipher' as s_origin
        from rdb$database
    )
    select
        a.s_origin
        ,encrypt( a.s_origin using aes mode ofb key '0123456789012345' iv 'abcdefghhgfedcba') as s_encrypted
    from a
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    S_ORIGIN                        Encrypts/decrypts data using symmetric cipher
    S_ENCRYPTED                     910805BDA8B05C475E8B5D3D0971D58649EA0D549FEA1633A8811429183E925E1C2C77CE4E3B9DCDFA0C75997E
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

