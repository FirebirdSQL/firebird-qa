#coding:utf-8
#
# id:           bugs.core_5728
# title:        When requesting the subtype of a NUMERIC or DECIMAL column with precision in [19, 34] using isc_info_sql_sub_type, it always returns 0, instead of 1 for NUMERIC and 2 for DECIMAL.
# decription:   
#                   Confirmed wrong result on: 4.0.0.918
#                   Checked on 4.0.0.943: OK, 1.235s.
#               
#                   30.10.2019. Adjusted expected-stdout to current FB, new datatype was introduced: numeric(38).
#                   Checked on: 4.0.0.1635.
#                   25.06.2020, 4.0.0.2076: changed types in SQLDA from numeric to int128 // after discuss with Alex about CORE-6342.
#                 
# tracker_id:   CORE-5728
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!sqltype).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test( 
        distance_num_1 numeric(19)
       ,distance_num_2 numeric(34)
       ,distance_dec_1 decimal(19)
       ,distance_dec_2 decimal(34)
    );
    commit;

    set sqlda_display on;
    select * from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 32752 INT128 Nullable scale: 0 subtype: 1 len: 16
    02: sqltype: 32752 INT128 Nullable scale: 0 subtype: 1 len: 16
    03: sqltype: 32752 INT128 Nullable scale: 0 subtype: 2 len: 16
    04: sqltype: 32752 INT128 Nullable scale: 0 subtype: 2 len: 16
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

