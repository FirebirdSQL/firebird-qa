#coding:utf-8

"""
ID:          issue-5640
ISSUE:       5640
TITLE:       Regression: (boolean) parameters as search condition no longer allowed
DESCRIPTION:
JIRA:        CORE-v
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table test(id int,boo boolean);
"""

db = db_factory(init=init_script)

test_script = """
    set sqlda_display on;
    set planonly;
    select * from test where ?;
    set planonly;
"""

act = isql_act('db', test_script)

expected_stdout = """
    INPUT message field count: 1
    01: sqltype: 32764 BOOLEAN scale: 0 subtype: 0 len: 1
      :  name:   alias:
      : table:   owner:

    PLAN (TEST NATURAL)

    OUTPUT message field count: 2
    01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
      :  name: ID  alias: ID
      : table: TEST  owner: SYSDBA
    02: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
      :  name: BOO  alias: BOO
      : table: TEST  owner: SYSDBA
"""

@pytest.mark.version('>=3.0.2')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

