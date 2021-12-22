#coding:utf-8
#
# id:           bugs.core_6294
# title:        Negative 128-bit integer constants are not accepted in DEFAULT clause
# decription:   
#                  Checked on 4.0.0.2104
#                
# tracker_id:   CORE-6294
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!sqltype|FIELD_).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    create domain dm_test as numeric(20,2) default -9999999999999999991; 
    create table test (x dm_test, y numeric(20,2) default -9999999999999999991);
    set sqlda_display on;
    insert into test default values returning x as field_x, y as field_y;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 32752 INT128 Nullable scale: -2 subtype: 1 len: 16
      : name: X alias: FIELD_X
    02: sqltype: 32752 INT128 Nullable scale: -2 subtype: 1 len: 16
      : name: Y alias: FIELD_Y

    FIELD_X                                               -9999999999999999991.00
    FIELD_Y                                               -9999999999999999991.00
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

