#coding:utf-8

"""
ID:          issue-2185
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/2185
TITLE:       Support hex numeric and string literals
DESCRIPTION:
    See:
        $FB_HOME/doc/sql.extensions/README.hex_literals.txt
        https://www.firebirdsql.org/file/documentation/chunk/en/refdocs/fblangref50/fblangref50-datatypes.html#fblangref50-datatypes-hex-literal
        https://www.firebirdsql.org/file/documentation/chunk/en/refdocs/fblangref50/fblangref50-commons.html#fblangref50-commons-hexstrings
        https://www.firebirdsql.org/file/documentation/chunk/en/refdocs/fblangref50/fblangref50-commons.html#fblangref50-commons-hexnumbers
JIRA:        CORE-1760
NOTES:
    [15.10.2026] pzotov
    Adjusted code to be performed in 6.x since introducing non-decimal integer literals, see:
    See notes in https://github.com/FirebirdSQL/firebird/pull/8564#issue-3059832235
        0x0 to 0x7FFFFFFFFF are positive INTEGER numbers with values from 0 to 2147483647
        0x80000000 to 0x7FFFFFFFFFFFFFFF are positive BIGINT numbers with values from 2147483648 to 9223372036854775807.
        0x8000000000000000 to 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF are positive INT128 numbers with values from 9223372036854775808 to 170141183460469231731687303715884105727
    Raised min_version to 4.0 because 3x not supports int128.
    Checked on 6.0.0.2211; 5.0.5.1906; 4.0.8.3328
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail OFF;
    set list on;

    -- binary literal ::=  { x | X } <quote> [ { <hexit> <hexit> }... ] <quote>

    -- must FAIL with token unknown '1' // because length is odd
    select x'1' as hex_01 from rdb$database;

    -- must pass:
    select x'11' as hex_11 from rdb$database;

    -- must pass:
    select x'0123456789' as hex_0123456789 from rdb$database;

    -- must pass:
    select x'01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789' as hex_long from rdb$database;

    -- must raise: token unknown because last char is not hexit
    select x'0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678x' as hex_invalid from rdb$database;

    -- must pass:
    select uuid_to_char(x'BA1749B583BF9146B360F54E25FE583E') as hex_uuid from rdb$database;

    -- ##############################################################################

    -- Numeric literal: { 0x | 0X } <hexit> [ <hexit>... ]
    -- https://firebirdsql.org/refdocs/langrefupd25-bigint.html

    -- https://github.com/FirebirdSQL/firebird/pull/8564#issue-3059832235
    -- 6x:
    -- 0x0 to 0x7FFFFFFFFF are positive INTEGER numbers with values from 0 to 2147483647
    -- 0x80000000 to 0x7FFFFFFFFFFFFFFF are positive BIGINT numbers with values from 2147483648 to 9223372036854775807.
    -- 0x8000000000000000 to 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF are positive INT128 numbers with values from 9223372036854775808 to 170141183460469231731687303715884105727

    recreate view v_test as
    select
        +-0x1              "+-0x1"              -- "-1(a)"
       ,-+-0xf             "-+-0xf"             -- "+15"
       ,0x7FFF             "0x7FFF"             -- "32767"
       ,0x8000             "0x8000"             -- "32768"
       ,0xFFFF             "0xFFFF"             -- "65535"
       ,0x10000            "0x10000"            -- "65536(a)"
       ,0x000000000010000  "0x000000000010000"  -- "65536(b)"
       ,0x7FFFFFFFFF       "0x7FFFFFFFFF"       -- 6x: positive INTEGER = 2147483647
       ,0x80000000         "0x80000000"         -- prior 6x: -2147483648;  6x: +2147483648
       ,0x080000000        "0x080000000"        -- "+2147483648(a)"
       ,0x000000080000000  "0x000000080000000"  -- "+2147483648(b)"
       ,0xFFFFFFFF         "0xFFFFFFFF"         -- "-1(b)"
       ,0x0FFFFFFFF        "0x0FFFFFFFF"        -- "+4294967295"
       ,0x100000000        "0x100000000"        -- "+4294967296(a)"
       ,0x0000000100000000 "0x0000000100000000" -- "+4294967296(b)"
       ,0x7FFFFFFFFFFFFFFF "0x7FFFFFFFFFFFFFFF" -- in all versions: +9223372036854775807
       ,0x8000000000000000 "0x8000000000000000" -- prior 6x: -9223372036854775808; 6x: positive INT128 = 9223372036854775808
       ,0x8000000000000001 "0x8000000000000001" -- "-9223372036854775807"
       ,0x8000000000000002 "0x8000000000000002" -- "-9223372036854775806"
       ,0xffffffffffffffff "0xffffffffffffffff" -- "-1(c)"
       ,0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF "0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" -- 6x: 170141183460469231731687303715884105727
    from rdb$database;

    select * from v_test;

    -- If the number of <hexit> is greater than 8, the constant data type is a signed BIGINT
    -- If it's less or equal than 8, the data type is a signed INTEGER
    set sqlda_display on;
    select * from v_test rows 0;
    set sqlda_display off;
"""

substitutions = [('.*At line.*', ''), ('-Token unknown.*', '-Token unknown'), ('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    if act.is_version('<6'):
        expected_sqlda = """
            INPUT message field count: 0
            OUTPUT message field count: 21
            01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: +-0x1  alias: +-0x1
            : table: V_TEST  owner: SYSDBA
            02: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: -+-0xf  alias: -+-0xf
            : table: V_TEST  owner: SYSDBA
            03: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0x7FFF  alias: 0x7FFF
            : table: V_TEST  owner: SYSDBA
            04: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0x8000  alias: 0x8000
            : table: V_TEST  owner: SYSDBA
            05: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0xFFFF  alias: 0xFFFF
            : table: V_TEST  owner: SYSDBA
            06: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0x10000  alias: 0x10000
            : table: V_TEST  owner: SYSDBA
            07: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x000000000010000  alias: 0x000000000010000
            : table: V_TEST  owner: SYSDBA
            08: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x7FFFFFFFFF  alias: 0x7FFFFFFFFF
            : table: V_TEST  owner: SYSDBA
            09: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0x80000000  alias: 0x80000000
            : table: V_TEST  owner: SYSDBA
            10: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x080000000  alias: 0x080000000
            : table: V_TEST  owner: SYSDBA
            11: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x000000080000000  alias: 0x000000080000000
            : table: V_TEST  owner: SYSDBA
            12: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0xFFFFFFFF  alias: 0xFFFFFFFF
            : table: V_TEST  owner: SYSDBA
            13: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x0FFFFFFFF  alias: 0x0FFFFFFFF
            : table: V_TEST  owner: SYSDBA
            14: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x100000000  alias: 0x100000000
            : table: V_TEST  owner: SYSDBA
            15: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x0000000100000000  alias: 0x0000000100000000
            : table: V_TEST  owner: SYSDBA
            16: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x7FFFFFFFFFFFFFFF  alias: 0x7FFFFFFFFFFFFFFF
            : table: V_TEST  owner: SYSDBA
            17: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x8000000000000000  alias: 0x8000000000000000
            : table: V_TEST  owner: SYSDBA
            18: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x8000000000000001  alias: 0x8000000000000001
            : table: V_TEST  owner: SYSDBA
            19: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x8000000000000002  alias: 0x8000000000000002
            : table: V_TEST  owner: SYSDBA
            20: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0xffffffffffffffff  alias: 0xffffffffffffffff
            : table: V_TEST  owner: SYSDBA
            21: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
            :  name: 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF  alias: 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            : table: V_TEST  owner: SYSDBA
        """
    else:
        expected_sqlda = """
            INPUT message field count: 0
            OUTPUT message field count: 21
            01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: +-0x1  alias: +-0x1
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            02: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: -+-0xf  alias: -+-0xf
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            03: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0x7FFF  alias: 0x7FFF
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            04: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0x8000  alias: 0x8000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            05: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0xFFFF  alias: 0xFFFF
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            06: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0x10000  alias: 0x10000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            07: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
            :  name: 0x000000000010000  alias: 0x000000000010000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            08: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x7FFFFFFFFF  alias: 0x7FFFFFFFFF
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            09: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x80000000  alias: 0x80000000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            10: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x080000000  alias: 0x080000000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            11: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x000000080000000  alias: 0x000000080000000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            12: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0xFFFFFFFF  alias: 0xFFFFFFFF
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            13: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x0FFFFFFFF  alias: 0x0FFFFFFFF
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            14: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x100000000  alias: 0x100000000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            15: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x0000000100000000  alias: 0x0000000100000000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            16: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
            :  name: 0x7FFFFFFFFFFFFFFF  alias: 0x7FFFFFFFFFFFFFFF
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            17: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
            :  name: 0x8000000000000000  alias: 0x8000000000000000
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            18: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
            :  name: 0x8000000000000001  alias: 0x8000000000000001
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            19: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
            :  name: 0x8000000000000002  alias: 0x8000000000000002
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            20: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
            :  name: 0xffffffffffffffff  alias: 0xffffffffffffffff
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
            21: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
            :  name: 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF  alias: 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            : table: V_TEST  schema: PUBLIC  owner: SYSDBA
        """

    expected_stdout_5x = f"""
        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown
        -'1'
        HEX_11                          11
        HEX_0123456789                  0123456789
        HEX_LONG                        01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown
        -'0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678x'
        HEX_UUID                        BA1749B5-83BF-9146-B360-F54E25FE583E
        +-0x1                           -1
        -+-0xf                          15
        0x7FFF                          32767
        0x8000                          32768
        0xFFFF                          65535
        0x10000                         65536
        0x000000000010000               65536
        0x7FFFFFFFFF                    549755813887
        0x80000000                      -2147483648
        0x080000000                     2147483648
        0x000000080000000               2147483648
        0xFFFFFFFF                      -1
        0x0FFFFFFFF                     4294967295
        0x100000000                     4294967296
        0x0000000100000000              4294967296
        0x7FFFFFFFFFFFFFFF              9223372036854775807
        0x8000000000000000              -9223372036854775808
        0x8000000000000001              -9223372036854775807
        0x8000000000000002              -9223372036854775806
        0xffffffffffffffff              -1
        0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF       170141183460469231731687303715884105727

        {expected_sqlda}
    """

    expected_stdout_6x = f"""
        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown
        -'1'
        HEX_11                          11
        HEX_0123456789                  0123456789
        HEX_LONG                        01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown
        -'0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678x'
        HEX_UUID                        BA1749B5-83BF-9146-B360-F54E25FE583E
        +-0x1                           -1
        -+-0xf                          15
        0x7FFF                          32767
        0x8000                          32768
        0xFFFF                          65535
        0x10000                         65536
        0x000000000010000               65536
        0x7FFFFFFFFF                    549755813887
        0x80000000                      2147483648
        0x080000000                     2147483648
        0x000000080000000               2147483648
        0xFFFFFFFF                      4294967295
        0x0FFFFFFFF                     4294967295
        0x100000000                     4294967296
        0x0000000100000000              4294967296
        0x7FFFFFFFFFFFFFFF              9223372036854775807
        0x8000000000000000                                        9223372036854775808
        0x8000000000000001                                        9223372036854775809
        0x8000000000000002                                        9223372036854775810
        0xffffffffffffffff                                       18446744073709551615
        0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF       170141183460469231731687303715884105727

        {expected_sqlda}
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
