#coding:utf-8
#
# id:           functional.datatypes.decfloat_parsing_scaled_integers_and_bigint_max_min
# title:        Interpretation of DECFLOAT values as BIGINT
# decription:   
#                   Check commit: "Fixed parsing of scaled integers and MAX/MIN INT64", 2017-05-28
#                   See: github.com/FirebirdSQL/firebird/commit/1278d0692b535f69c7f9e208aad9682980ed9c59
#                   40SS, build 4.0.0.680: OK, 1.047s;  build 4.0.0.651: FAILED.
#               
#                   10.12.2019. Updated syntax for SET BIND command because it was changed in 11-nov-2019. 
#                   Checked on: WI-T4.0.0.1685.
#               
#                   30.12.2019. Updated code and expected_stdout - get it from Alex, see letter 30.12.2019 16:15.
#                   Checked on: 4.0.0.1712: OK, 1.188s
#               
#                   25.06.2020, 4.0.0.2076: changed types in SQLDA from numeric to int128 // after discuss with Alex about CORE-6342.
#                   01.07.2020, 4.0.0.2084: adjusted expected output ('subtype' values).
#                   Removed unnecessary lines from output and added substitution section for result to be properly filtered.
#               
#                   ::: NOTE :::
#                   Found a problem with interpreting values
#                   170141183460469231731687303715884105727 and -170141183460469231731687303715884105728
#                   Sent letter to Alex (01.07.2020 13:55), waiting for fix. Check of bind DECFLOAT to INT128 was deferred.
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!sqltype|BEHIND_BIGINT_|BIGINT_|DROB1).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
     set list on;
     set sqlda_display on;

     recreate view v_test as
     select
        -9223372036854775809 as behind_bigint_min
        ,9223372036854775808 as behind_bigint_max
        ,-9223372036854775808 as bigint_min
        ,9223372036854775807 as bigint_max
        ,0.0123456789123456789 as drob1
     from rdb$database;

     select * from  v_test;

     set bind of bigint to double precision;
     set sqlda_display off;

     select * from  v_test;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
    :  name: BEHIND_BIGINT_MIN  alias: BEHIND_BIGINT_MIN
    02: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
    :  name: BEHIND_BIGINT_MAX  alias: BEHIND_BIGINT_MAX
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    :  name: BIGINT_MIN  alias: BIGINT_MIN
    04: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    :  name: BIGINT_MAX  alias: BIGINT_MAX
    05: sqltype: 580 INT64 Nullable scale: -19 subtype: 0 len: 8
    :  name: DROB1  alias: DROB1
    BEHIND_BIGINT_MIN                                        -9223372036854775809
    BEHIND_BIGINT_MAX                                         9223372036854775808
    BIGINT_MIN                      -9223372036854775808
    BIGINT_MAX                      9223372036854775807
    DROB1                           0.0123456789123456789
    BEHIND_BIGINT_MIN                                        -9223372036854775809
    BEHIND_BIGINT_MAX                                         9223372036854775808
    BIGINT_MIN                      -9.223372036854776e+18
    BIGINT_MAX                      9.223372036854776e+18
    DROB1                           0.01234567891234568
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

