#coding:utf-8

"""
ID:          issue-2165
ISSUE:       2165
TITLE:       Field subtype of DEC_FIXED columns not returned by isc_info_sql_sub_type
DESCRIPTION:
  When requesting the subtype of a NUMERIC or DECIMAL column with precision in [19, 34]
  using isc_info_sql_sub_type, it always returns 0, instead of 1 for NUMERIC and 2 for DECIMAL.
NOTES:
[30.10.2019]
  Adjusted expected-stdout to current FB, new datatype was introduced: numeric(38).
[25.06.2020]
  4.0.0.2076: changed types in SQLDA from numeric to int128 // after discuss with Alex about CORE-6342.
JIRA:        CORE-5728
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script, substitutions=[('^((?!sqltype).)*$', ''), ('[ \t]+', ' ')])

expected_stdout = """
    01: sqltype: 32752 INT128 Nullable scale: 0 subtype: 1 len: 16
    02: sqltype: 32752 INT128 Nullable scale: 0 subtype: 1 len: 16
    03: sqltype: 32752 INT128 Nullable scale: 0 subtype: 2 len: 16
    04: sqltype: 32752 INT128 Nullable scale: 0 subtype: 2 len: 16
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
