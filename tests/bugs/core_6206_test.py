#coding:utf-8
#
# id:           bugs.core_6206
# title:        VARCHAR of insufficient length used for set bind of decfloat to varchar
# decription:
#                   Confirmed bug on 4.0.0.1685
#                   Checked on 4.0.0.1691: OK, 1.165s.
#
#                   26.06.2020: changed SET BIND argument from numeric(38) to INT128, adjusted output
#                   (letter from Alex, 25.06.2020 17:56; needed after discuss CORE-6342).
#                   Checked on 4.0.0.2078.
#
# tracker_id:   CORE-6206
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('charset.*', ''), ('^((?!(sqltype)).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set list on;

    set bind of decfloat to char;
    select -1.234567890123456789012345678901234E+6144 as decfloat_to_char from rdb$database;

    set bind of decfloat to varchar;
    select -1.234567890123456789012345678901234E+6144 as decfloat_to_varchar from rdb$database;

    --set bind of numeric(38) to char;
    set bind of int128 to char;
    select 12345678901234567890123456789012345678 as n38_to_char from rdb$database;

    --set bind of numeric(38) to varchar;
    set bind of int128 to char;
    select 12345678901234567890123456789012345678 as n38_to_varchar from rdb$database;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 452 TEXT scale: 0 subtype: 0 len: 42
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 42
    01: sqltype: 452 TEXT scale: 0 subtype: 0 len: 47
    01: sqltype: 452 TEXT scale: 0 subtype: 0 len: 47
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.charset = 'NONE'
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

