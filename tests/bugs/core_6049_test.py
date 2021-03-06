#coding:utf-8
#
# id:           bugs.core_6049
# title:        Builtin functions converting binary string to hexadecimal representation and vice versa
# decription:   
#                   Test may need to be more complex. Currently only basic operations are checked:
#                   * ability to insert into binary field result of hex_decode()
#                   * result of double conversion: bin_data -> base64_encode -> base64_decode 
#                     - must be equal to initial bin_data (and similar for bin_data -> hex_encode -> hex_decode)
#                   We get columns type details using sqlda_display in order to fix them in expected_stdout.
#               
#                   Checked on 4.0.0.1496: OK, 1.679s.
#                
# tracker_id:   CORE-6049
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('INPUT message.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    recreate table test(uid binary(20));
    commit;
    insert into test(uid) values( hex_decode(_octets 'CFA677DA45594D52A7D24EF9FA4C04D600000000') );
    commit;

    set list on;
    set sqlda_display on;
    select 
        t.*
       ,uid = "b64_decode(b64_encode(uid))" as "b64_dec(b64_enc(uid)) result"
       ,uid = "hex_decode(hex_encode(uid))" as "hex_dec(hex_enc(uid)) result"
    from (
        select 
            uid
           ,base64_encode(uid) as "b64_encode(uid)"
           ,base64_decode(base64_encode(uid)) as "b64_decode(b64_encode(uid))"
           ,hex_encode(uid) as "hex_encode(uid)"
           ,hex_decode(hex_encode(uid)) as "hex_decode(hex_encode(uid))"
        from test
    ) t;

    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    OUTPUT message field count: 7
    01: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 20 charset: 1 OCTETS
      :  name: UID  alias: UID
      : table: TEST  owner: SYSDBA
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 28 charset: 2 ASCII
      :  name:   alias: b64_encode(uid)
      : table:   owner:
    03: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 21 charset: 1 OCTETS
      :  name:   alias: b64_decode(b64_encode(uid))
      : table:   owner:
    04: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 40 charset: 2 ASCII
      :  name:   alias: hex_encode(uid)
      : table:   owner:
    05: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 20 charset: 1 OCTETS
      :  name:   alias: hex_decode(hex_encode(uid))
      : table:   owner:
    06: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
      :  name:   alias: b64_dec(b64_enc(uid)) result
      : table:   owner:
    07: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
      :  name:   alias: hex_dec(hex_enc(uid)) result
      : table:   owner:

    UID                             CFA677DA45594D52A7D24EF9FA4C04D600000000
    b64_encode(uid)                 z6Z32kVZTVKn0k75+kwE1gAAAAA=
    b64_decode(b64_encode(uid))     CFA677DA45594D52A7D24EF9FA4C04D600000000
    hex_encode(uid)                 CFA677DA45594D52A7D24EF9FA4C04D600000000
    hex_decode(hex_encode(uid))     CFA677DA45594D52A7D24EF9FA4C04D600000000
    b64_dec(b64_enc(uid)) result    <true>
    hex_dec(hex_enc(uid)) result    <true>
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

