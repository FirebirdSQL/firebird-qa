#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9115
TITLE:       A trailing garbage character is accepted after a special date/time expression
DESCRIPTION:
NOTES:
    [09.08.2026] pzotov
    Confirmed bug on 6.0.0.2120-2e16c7c.
    Checked on 6.0.0.2126-a8b87b4.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    select cast('now)' as timestamp) from rdb$database;
    select cast('tomorrow;' as date) from rdb$database;
    select cast('today!' as date) from rdb$database;
    select cast('yesterday-' as date) from rdb$database;
"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    Statement failed, SQLSTATE = 22018
    conversion error from string "now)"
    
    Statement failed, SQLSTATE = 22018
    conversion error from string "tomorrow;"
    
    Statement failed, SQLSTATE = 22018
    conversion error from string "today!"
    
    Statement failed, SQLSTATE = 22018
    conversion error from string "yesterday-"
"""

@pytest.mark.version('>=6')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
