#coding:utf-8
#
# id:           bugs.core_6291
# title:        Statement "CREATE DOMAIN [dm_name] as BIGINT" raises "numeric value is out of range" if its default value is -9223372036854775808
# decription:   
#                   Checked on 4.0.0.2100 - all OK.
#                   (intermediate snapshot with timestamp: 10.07.20 11:44)
#                
# tracker_id:   CORE-6291
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    create domain dm_bigint_absolute_max as bigint default 9223372036854775807;
    create domain dm_bigint_absolute_min as bigint default -9223372036854775808;
    create domain dm_int128_absolute_max as int128 default  170141183460469231731687303715884105727;
    create domain dm_int128_absolute_min as int128 default -170141183460469231731687303715884105728;

    create table test1(
        n_bigint_absol_max    bigint default 9223372036854775807
       ,n_bigint_absol_min    bigint default -9223372036854775808
       ,n_int128_absol_max    int128 default  170141183460469231731687303715884105727
       ,n_int128_absol_min    int128 default -170141183460469231731687303715884105728
       ,n_dm_bigint_absol_max dm_bigint_absolute_max
       ,n_dm_bigint_absol_min dm_bigint_absolute_min
       ,n_dm_int128_absol_max dm_int128_absolute_max
       ,n_dm_int128_absol_min dm_int128_absolute_min
    );
    commit;

    insert into test1 default values;
    select * from test1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    N_BIGINT_ABSOL_MAX              9223372036854775807
    N_BIGINT_ABSOL_MIN              -9223372036854775808
    N_INT128_ABSOL_MAX                    170141183460469231731687303715884105727
    N_INT128_ABSOL_MIN                   -170141183460469231731687303715884105728
    N_DM_BIGINT_ABSOL_MAX           9223372036854775807
    N_DM_BIGINT_ABSOL_MIN           -9223372036854775808
    N_DM_INT128_ABSOL_MAX                 170141183460469231731687303715884105727
    N_DM_INT128_ABSOL_MIN                -170141183460469231731687303715884105728
  """

@pytest.mark.version('>=4.0')
def test_core_6291_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

