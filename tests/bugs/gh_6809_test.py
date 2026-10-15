#coding:utf-8

"""
ID:          issue-6809
ISSUE:       6809
TITLE:       Integer hex-literals: support for INT128
DESCRIPTION:
    See:
        $FB_HOME/doc/sql.extensions/README.hex_literals.txt
        https://www.firebirdsql.org/file/documentation/chunk/en/refdocs/fblangref50/fblangref50-datatypes.html#fblangref50-datatypes-hex-literal
        https://www.firebirdsql.org/file/documentation/chunk/en/refdocs/fblangref50/fblangref50-commons.html#fblangref50-commons-hexstrings
        https://www.firebirdsql.org/file/documentation/chunk/en/refdocs/fblangref50/fblangref50-commons.html#fblangref50-commons-hexnumbers
NOTES:
    [27.07.2021] pzotov
    NB: currently multiplication leads to following:
      int64 * int64 => int128
      int64 * int32 => int64
    In some cases one need to make explicit CAST of result to int128.
    For example, following attempts to evaluate result of multiplication -1 * (-9223372036854775808)
    will fail with integer overflow: -0x8000000000000000, -(0x8000000000000000); -1*(0x8000000000000000).
    Attempt to apply unary minus to -2^127 leads to "SQLSTATE = 22018 / conversion error from string".

    Discussed with Alex and dimitr 17-18 may 2021.
    Adjusted expected* sections to results in current snapshots FB 4.x and 5.x: this is needed since fix #6874

    [15.10.2026] pzotov
    Adjusted code to be performed in 6.x since introducing non-decimal integer literals, see:
    See notes in https://github.com/FirebirdSQL/firebird/pull/8564#issue-3059832235
        0x0 to 0x7FFFFFFFFF are positive INTEGER numbers with values from 0 to 2147483647
        0x80000000 to 0x7FFFFFFFFFFFFFFF are positive BIGINT numbers with values from 2147483648 to 9223372036854775807.
        0x8000000000000000 to 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF are positive INT128 numbers with values from 9223372036854775808 to 170141183460469231731687303715884105727
    Checked on 6.0.0.2211; 5.0.5.1906; 4.0.8.3328
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail OFF;
    set list on;
    set sqlda_display on;
    --select 0xF0000000 as "0xF0000000" from rdb$database; -- 496 LONG len: 4

    -- "If the number of <hexit> is less or equal than 8, the data type is a signed INTEGER"
    -- 496 LONG len: 4:
    select  0x7FFFFFFF  as "hex +0x7FFFFFFF" from rdb$database;   --  2147483647

    -- ::: ACHTUNG :::
    -- prior 6x: 496  LONG len: 4, value: -2147483648
    -- 6.0.0.2190-afba279: 580 INT64 len: 8, value: +2147483648 // "0x80000000 to ... are positive BIGINT numbers"
    select  0x80000000  as "hex +0x80000000" from rdb$database;

    -- expected: 580 INT64 scale: 0 subtype: 0 len: 8; value: +2147483648
    select -0x80000000  as "hex -0x80000000" from rdb$database;         -- -2147483648 - NEGATIVE number!
    select -(0x80000000)  as "hex -(0x80000000)" from rdb$database;     -- -2147483648 - NEGATIVE number!
    
    -- ::: ACHTUNG  :::
    -- prior 6x:   580  INT64 len: 8,  result: +2147483648
    -- 6.0.0.2190-afba279: 32752 INT128 len: 16, result: -2147483648
    select -1*(0x80000000)  as "hex -1*(0x80000000)" from rdb$database;

    ------------------
    -- "If the number of <hexit> is greater than 8, the constant data type is a signed BIGINT"
    -- prior 6x: 580 INT64 len: 8
    -- 6.0.0.2190-afba279: 496 LONG  len: 4 // "0x0 to 0x7FFFFFFFFF are positive INTEGER ... 0 to 2147483647"
    select  0x07FFFFFFF as "hex +0x07FFFFFFF" from rdb$database;  -- +2147483647

    -- prior 6x: 580 INT64 len: 8
    -- 6.0.0.2190-afba279: 496 LONG  len: 4 // "0x0 to 0x7FFFFFFFFF are positive INTEGER ... 0 to 2147483647"
    select -0x07FFFFFFF as "hex -0x07FFFFFFF" from rdb$database;  -- -2147483647

    select  0x080000000 as "hex +0x080000000" from rdb$database;  --  2147483648
    select -0x080000000 as "hex -0x080000000" from rdb$database;  -- -2147483648

    select  0x100000000 as "hex +0x100000000" from rdb$database;  --  4294967296
    select -0x100000000 as "hex -0x100000000" from rdb$database;  -- -4294967296

    select  0x7FFFFFFFFFFFFFFF as "hex +0x7FFFFFFFFFFFFFFF" from rdb$database;  --  9223372036854775807

    select -0x7FFFFFFFFFFFFFFF as "hex -0x7FFFFFFFFFFFFFFF" from rdb$database;  -- -9223372036854775807

    -- ::: ACHTUNG  :::
    -- prior 6x: 580 INT64 len: 8,               value: -9223372036854775808
    -- 6.0.0.2190-afba279: 32752 INT128 len: 16, value: +9223372036854775808 // 0x8000000000000000 to ... are positive INT128  9223372036854775808 to 170141183460469231731687303715884105727
    select  0x8000000000000000 as "hex +0x8000000000000000" from rdb$database;

    -- ::: NB-2 :::
    -- prior 6x: SQLSTATE = 22003 / Integer overflow.  The result of an integer operation caused the most significant bit of the result to carry.
    -- 6.0.0.2190-afba279: 580 INT64 len: 8, value: -9223372036854775808
    select -0x8000000000000000 as "hex -0x8000000000000000" from rdb$database;

    select -(0x8000000000000000) as "hex -0x8000000000000000" from rdb$database; -- SQLSTATE = 22003
    select -1*(0x8000000000000000) as "hex -1*(0x8000000000000000)" from rdb$database; -- SQLSTATE = 22003

    select  0x8000000000000001 as "hex +0x8000000000000001" from rdb$database; -- -9223372036854775807
    select  0xFFFFFFFFFFFFFFFF as "hex +0xFFFFFFFFFFFFFFFF" from rdb$database; -- -1


    ------------------
    -- "literals of 9-16 hex-pairs -> INT128"
    -- 32752 INT128 scale: 0 subtype: 0 len: 16
    select  0x07FFFFFFFFFFFFFFF as "hex +0x07FFFFFFFFFFFFFFF" from rdb$database;  -- 9223372036854775807

    -- ::: NB-3 :::
    -- Statement failed, SQLSTATE = 22018 / conversion error from string
    -- rather than "32752 INT128 scale: 0 subtype: 0 len: 16; value: -9223372036854775807"
    select -0x07FFFFFFFFFFFFFFF as "hex -0x07FFFFFFFFFFFFFFF" from rdb$database; -- SQLSTATE = 22018
    select -(0x07FFFFFFFFFFFFFFF) as "hex -(0x07FFFFFFFFFFFFFFF)" from rdb$database; -- SQLSTATE = 22018
    select -1*(0x07FFFFFFFFFFFFFFF) as "hex -1*(0x07FFFFFFFFFFFFFFF)" from rdb$database; -- -9223372036854775807 // OK


    select  0x08000000000000000 as "hex +0x08000000000000000" from rdb$database;  -- 9223372036854775808

    select  0x7FFFFFFFFFFFFFFF0 as "hex +0x7FFFFFFFFFFFFFFF0" from rdb$database;  -- 147573952589676412912

    select 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF as "hex 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" from rdb$database; -- 170141183460469231731687303715884105727
    select 0x80000000000000000000000000000000 as "hex 0x80000000000000000000000000000000" from rdb$database; -- -170141183460469231731687303715884105728

    -- ::: NB-4 :::
    -- Statement failed, SQLSTATE = 22018 / conversion error from string
    -- rather than "32752 INT128 scale: 0 subtype: 0 len: 16; value: -170141183460469231731687303715884105727"
    select -0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF as "hex 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" from rdb$database;
    select -(0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) as "hex -(0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)" from rdb$database;
    select -1*(0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) as "hex -1*(0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)" from rdb$database; -- -170141183460469231731687303715884105727 // OK

    -- Statement failed, SQLSTATE = 22018
    -- conversion error from string
    select -0x80000000000000000000000000000000 as "hex 0x80000000000000000000000000000000" from rdb$database;

    -- ::: NB-5 :::
    -- Expected:
    -- actual: -170141183460469231731687303715884105727
    select 0x80000000000000000000000000000001 as "hex 0x80000000000000000000000000000001" from rdb$database;

    select 0x70000000000000000000000000000001 as "hex +0x70000000000000000000000000000001" from rdb$database; -- +191408831393027885698148216680369618943
    select 0x8FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF as "hex +0x8FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" from rdb$database; -- -191408831393027885698148216680369618943
    select 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF as "hex +0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" from rdb$database; -- ?? -1 ?? // 340282366920938463463374607431768211455

    -- ::: NB-6 :::
    -- "SQLSTATE = 42000 / Dynamic SQL Error / -Token unknown / -as"
    -- (because number of hex pairs exceeds 16):
    select 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF as "hex +0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" from rdb$database;
    select 0x0000000000000000000000000000000000 as "hex +0x0000000000000000000000000000000000" from rdb$database;
    --------------------


    select 0x8FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF + 0x70000000000000000000000000000001 as "hex sum_01" from rdb$database; -- 0

    select 0x7FFFFFFF - 0x70000000000000000000000000000001 as "hex sub_01" from rdb$database;

    --select 36000/-4000/300 d from rdb$database;
    select 0x8ca0 / -0xfa0 / 3 as "hex div_01" from rdb$database;

    select 0x688589CC0E9505E2F2FEE5580000000
           / 0x2
           / 0x3
           / 0x4
           / 0x5
           / 0x6
           / 0x7
           / 0x8
           / 0x9
           / 0xa
           / 0xb
           / 0xc
           / 0xd
           / 0xe
           / 0xf
           / 0x10
           / 0x11
           / 0x12
           / 0x13
           / 0x14
           / 0x15
           / 0x16
           / 0x17
           / 0x18
           / 0x19
           / 0x1a
           / 0x1b
           / 0x1c
           / 0x1d
           / 0x1e
           / 0x1f
           / 0x20
     as "hex 33!/32!"
     from rdb$database;
"""

'''
substitutions = [ 
                  ('^((?!(SQLSTATE|sqltype|hex)).)*$', ''),
                  ('(-)?Token unknown.*', 'Token unknown'),
                  Overflow of the number
                  Integer overflow
                  conversion error 
                  ('[ \t]+', ' ')
                ]
'''
substitutions = [ 
                   (r':\s+name: ', 'name: ')
                  ,('alias:.*', '')
                  ,(r'^\s*name:.*', '')
                  ,(r':\s+table:\s+(schema:\s+)?owner:.*', '')
                  ,('(INPUT|OUTPUT) message.*', '')
                  ,('[ \t]+', ' ')
                ]
act = isql_act('db', test_script, substitutions = substitutions)


#############
###   4x  ###
#############
expected_stdout_4x = """
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex +0x7FFFFFFF 2147483647
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex +0x80000000 -2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -0x80000000 -2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -(0x80000000) -2147483648
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -1*(0x80000000) 2147483648
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x07FFFFFFF 2147483647
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x07FFFFFFF -2147483647
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x080000000 2147483648
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x080000000 -2147483648
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x100000000 4294967296
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x100000000 -4294967296
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x7FFFFFFFFFFFFFFF 9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x7FFFFFFFFFFFFFFF -9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x8000000000000000 -9223372036854775808
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    Statement failed, SQLSTATE = 22003
    Integer overflow. The result of an integer operation caused the most significant bit of the result to carry.
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    Statement failed, SQLSTATE = 22003
    Integer overflow. The result of an integer operation caused the most significant bit of the result to carry.
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x8000000000000000) 9223372036854775808
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x8000000000000001 -9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0xFFFFFFFFFFFFFFFF -1
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x07FFFFFFFFFFFFFFF 9223372036854775807
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X07FFFFFFFFFFFFFFF"
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X07FFFFFFFFFFFFFFF"
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x07FFFFFFFFFFFFFFF) -9223372036854775807
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x08000000000000000 9223372036854775808
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x7FFFFFFFFFFFFFFF0 147573952589676412912
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF 170141183460469231731687303715884105727
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 0x80000000000000000000000000000000 -170141183460469231731687303715884105728
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) -170141183460469231731687303715884105727
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X80000000000000000000000000000000"
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 0x80000000000000000000000000000001 -170141183460469231731687303715884105727
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x70000000000000000000000000000001 148873535527910577765226390751398592513
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x8FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF -148873535527910577765226390751398592513
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF -1
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 1, column 44
    -as
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 1, column 45
    -as
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex sum_01 0
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex sub_01 -148873535527910577765226390749251108866
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex div_01 -3
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 33!/32! 33
"""

#############
###   5x  ###
#############
expected_stdout_5x = """
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex +0x7FFFFFFF 2147483647
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex +0x80000000 -2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -0x80000000 -2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -(0x80000000) -2147483648
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -1*(0x80000000) 2147483648
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x07FFFFFFF 2147483647
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x07FFFFFFF -2147483647
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x080000000 2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -0x080000000 -2147483648
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x100000000 4294967296
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x100000000 -4294967296
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x7FFFFFFFFFFFFFFF 9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x7FFFFFFFFFFFFFFF -9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x8000000000000000 -9223372036854775808
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    Statement failed, SQLSTATE = 22003
    Integer overflow. The result of an integer operation caused the most significant bit of the result to carry.
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    Statement failed, SQLSTATE = 22003
    Integer overflow. The result of an integer operation caused the most significant bit of the result to carry.
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x8000000000000000) 9223372036854775808
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x8000000000000001 -9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0xFFFFFFFFFFFFFFFF -1
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x07FFFFFFFFFFFFFFF 9223372036854775807
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X07FFFFFFFFFFFFFFF"
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X07FFFFFFFFFFFFFFF"
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x07FFFFFFFFFFFFFFF) -9223372036854775807
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x08000000000000000 9223372036854775808
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x7FFFFFFFFFFFFFFF0 147573952589676412912
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF 170141183460469231731687303715884105727
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 0x80000000000000000000000000000000 -170141183460469231731687303715884105728
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) -170141183460469231731687303715884105727
    Statement failed, SQLSTATE = 22018
    conversion error from string "-0X80000000000000000000000000000000"
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 0x80000000000000000000000000000001 -170141183460469231731687303715884105727
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x70000000000000000000000000000001 148873535527910577765226390751398592513
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x8FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF -148873535527910577765226390751398592513
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF -1
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 1, column 44
    -as
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 1, column 45
    -as
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex sum_01 0
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex sub_01 -148873535527910577765226390749251108866
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex div_01 -3
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 33!/32! 33
"""

#############
###   6x  ###
#############
expected_stdout_6x = """
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex +0x7FFFFFFF 2147483647
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x80000000 2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -0x80000000 -2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -(0x80000000) -2147483648
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x80000000) -2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex +0x07FFFFFFF 2147483647
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -0x07FFFFFFF -2147483647
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x080000000 2147483648
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex -0x080000000 -2147483648
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x100000000 4294967296
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x100000000 -4294967296
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x7FFFFFFFFFFFFFFF 9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x7FFFFFFFFFFFFFFF -9223372036854775807
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x8000000000000000 9223372036854775808
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x8000000000000000 -9223372036854775808
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x8000000000000000 -9223372036854775808
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x8000000000000000) -9223372036854775808
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x8000000000000001 9223372036854775809
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0xFFFFFFFFFFFFFFFF 18446744073709551615
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex +0x07FFFFFFFFFFFFFFF 9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -0x07FFFFFFFFFFFFFFF -9223372036854775807
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    hex -(0x07FFFFFFFFFFFFFFF) -9223372036854775807
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x07FFFFFFFFFFFFFFF) -9223372036854775807
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x08000000000000000 9223372036854775808
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x7FFFFFFFFFFFFFFF0 147573952589676412912
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF 170141183460469231731687303715884105727
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 2, column 12
    -Overflow of the number
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF -170141183460469231731687303715884105727
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -(0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) -170141183460469231731687303715884105727
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex -1*(0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) -170141183460469231731687303715884105727
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 5, column 13
    -Overflow of the number
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 4, column 12
    -Overflow of the number
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex +0x70000000000000000000000000000001 148873535527910577765226390751398592513
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 2, column 12
    -Overflow of the number
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 2, column 12
    -Overflow of the number
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 6, column 12
    -Overflow of the number
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    hex +0x0000000000000000000000000000000000 0
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 4, column 12
    -Overflow of the number
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex sub_01 -148873535527910577765226390749251108866
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex div_01 -3
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    hex 33!/32! 33
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_4x if act.is_version('<5') else expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
