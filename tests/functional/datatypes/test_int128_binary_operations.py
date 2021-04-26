#coding:utf-8
#
# id:           functional.datatypes.int128_binary_operations
# title:        Basic test for binary functions against INT128 datatype
# decription:   
#                   Test verifies https://github.com/FirebirdSQL/firebird/commit/137c3a96e51b8bc34cb74732687067e96c971226
#                   (Postfix for CORE-6342: enable support of int128 in bin_* family of functions).
#                   Checked on 4.0.0.2083 (intermediate build 30.06.2020 16:38).
#                
# tracker_id:   
# min_versions: ['4.0.0']
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
    set heading off;
    recreate table test_i128(bi_least int128, bi_great int128);
    commit;

    insert into test_i128(bi_least, bi_great) values(-170141183460469231731687303715884105728, 170141183460469231731687303715884105727);


    -- All subsequent expressions before 4.0.0.2083 raised:
    -- Statement failed, SQLSTATE = 22003
    -- arithmetic exception, numeric overflow, or string truncation
    -- -Integer overflow.  The result of an integer operation caused the most significant bit of the result to carry.

    select bin_and(bi_least,bi_great) from test_i128; -- expected: 0
    select bin_not(bi_least) from test_i128; -- expected: 170141183460469231731687303715884105727
    select bin_not(bi_great) from test_i128; -- expected: -170141183460469231731687303715884105728
    select bin_or(bi_least, bi_great) from test_i128; -- expected: -1
    select bin_shr(bi_least,127) from test_i128;  -- expected: 1
    select bin_shr(bi_great,127) from test_i128;  -- expected: 0
    select bin_shl(bi_least,127) from test_i128; -- expected: 0
    select bin_and( bin_shl(bi_great,127), bi_least) from test_i128; -- expected: -170141183460469231731687303715884105728
    select bin_xor(bi_least, bi_great) from test_i128; -- expected: -1
    select bin_xor(bi_least, bi_great) from test_i128; -- expected: -1
    select bin_xor(bi_least, bin_xor(bi_least, bi_great)) from test_i128; -- expected: 170141183460469231731687303715884105727
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    0
    170141183460469231731687303715884105727
    -170141183460469231731687303715884105728
    -1
    1
    0
    0
    -170141183460469231731687303715884105728
    -1
    -1
    170141183460469231731687303715884105727
  """

@pytest.mark.version('>=4.0')
def test_int128_binary_operations_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

