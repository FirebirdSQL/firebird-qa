#coding:utf-8

"""
ID:          issue-7698
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7698
TITLE:       The legacy plan with window functions is broken
DESCRIPTION:
NOTES:
    Confirmed bug on 5.0.0.1149
    Checked on 5.0.0.1155 -- all OK.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = f"""
    set plan on;
    set planonly;
    select count(*) over() from rdb$relations;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (RDB$RELATIONS NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
