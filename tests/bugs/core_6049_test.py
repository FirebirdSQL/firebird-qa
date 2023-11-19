#coding:utf-8

"""
ID:          issue-6299
ISSUE:       6299
TITLE:       Builtin functions converting binary string to hexadecimal representation and vice versa
DESCRIPTION:
  Test may need to be more complex. Currently only basic operations are checked:
  * ability to insert into binary field result of hex_decode()
  * result of double conversion: bin_data -> base64_encode -> base64_decode
    - must be equal to initial bin_data (and similar for bin_data -> hex_encode -> hex_decode)
  We get columns type details using sqlda_display in order to fix them in expected_stdout.
JIRA:        CORE-6049
FBTEST:      bugs.core_6049
NOTES:
    [19.11.2023] pzotov
    Adjusted expected_stdout because SQLDA output changed after
        0b846ad4787233559d371ade99776b4e1da205b7 // 4.x
        1ed7f81f168b643a29357fce2e1f49156e9f5a1f // 5.x
        ab6aced05723dc1b2e6bb96bfdaa86cb3090daf2 // 6.x
    (Log message: "correction metaData")
    Discussed with dimitr, letter 20.11.2023 17:38.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

substitutions = [ ('^((?!(sqltype|alias|UID|encode|decode|result)).)*$', ''), ]

act = isql_act('db', test_script, substitutions = substitutions)

COMMON_OUTPUT = """
    UID                             CFA677DA45594D52A7D24EF9FA4C04D600000000
    b64_encode(uid)                 z6Z32kVZTVKn0k75+kwE1gAAAAA=
    b64_decode(b64_encode(uid))     CFA677DA45594D52A7D24EF9FA4C04D600000000
    hex_encode(uid)                 CFA677DA45594D52A7D24EF9FA4C04D600000000
    hex_decode(hex_encode(uid))     CFA677DA45594D52A7D24EF9FA4C04D600000000
    b64_dec(b64_enc(uid)) result    <true>
    hex_dec(hex_enc(uid)) result    <true>
"""

expected_stdout = f"""
    01: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 20 charset: 1 OCTETS
    :  name: UID  alias: UID
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 28 charset: 2 ASCII
    :  name: BASE64_ENCODE  alias: b64_encode(uid)
    03: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 21 charset: 1 OCTETS
    :  name: BASE64_DECODE  alias: b64_decode(b64_encode(uid))
    04: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 40 charset: 2 ASCII
    :  name: HEX_ENCODE  alias: hex_encode(uid)
    05: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 20 charset: 1 OCTETS
    :  name: HEX_DECODE  alias: hex_decode(hex_encode(uid))
    06: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
    :  name:   alias: b64_dec(b64_enc(uid)) result
    07: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
    :  name:   alias: hex_dec(hex_enc(uid)) result
    {COMMON_OUTPUT}
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
