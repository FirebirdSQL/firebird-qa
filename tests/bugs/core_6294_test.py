#coding:utf-8

"""
ID:          issue-6536
ISSUE:       6536
TITLE:       Negative 128-bit integer constants are not accepted in DEFAULT clause
DESCRIPTION:
JIRA:        CORE-6294
FBTEST:      bugs.core_6294
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    create domain dm_test as numeric(20,2) default -9999999999999999991;
    create table test (x dm_test, y numeric(20,2) default -9999999999999999991);
    set sqlda_display on;
    insert into test default values returning x as field_x, y as field_y;
"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype|FIELD_).)*$', ''), ('[ \t]+', ' ')])

expected_stdout = """
    01: sqltype: 32752 INT128 Nullable scale: -2 subtype: 1 len: 16
      : name: X alias: FIELD_X
    02: sqltype: 32752 INT128 Nullable scale: -2 subtype: 1 len: 16
      : name: Y alias: FIELD_Y

    FIELD_X                                               -9999999999999999991.00
    FIELD_Y                                               -9999999999999999991.00
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
