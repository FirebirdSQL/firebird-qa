#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/7641d759a9b26d73dc2d24a47734a1a3a00a0a8a
TITLE:       Fix modulo crash on MIN % -1
DESCRIPTION:
    FB crashes on attempt to evaluate MIN_BIGINT % -1 (i.e. -9223372036854775808 % -1).
    No crashes occur for values like -9223372036854775807 or -9223372036854775809 (int128) or -2E127.
NOTES:
    [01.07.2026] pzotov
    Confirmed crash on 6.0.0.2035 and all 3.x ... 5.x.
    Checked on 6.0.0.2050.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    select mod(-9223372036854775808, -1) as chk_modulo from rdb$database;
"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    CHK_MODULO 0
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
