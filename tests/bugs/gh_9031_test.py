#coding:utf-8

"""
ID:          n/a
ISSUE:       https://groups.google.com/g/firebird-devel/c/Hr9Y9bnGTqY
TITLE:       Segfault after package body drop
DESCRIPTION:
    FB crashed since #7589a56a (introductions of package constants, #8916).
NOTES:
    [23.05.2026] pzotov
    Script below seems the minimal case to reproduce problem (no any line must be removed from it).
    Bug was found occasionally when analyzing reason of replication tests fails at final stage (when all DB opbjects are removed).
    See email messages 27.07.2026 1715 ("-Function 10 not found"); 16.05.2026 1758, 17.05.2026 0009.
    Confirmed bug (crash) on 6.0.0.1954.
    Checked on 6.0.0.1965 -- all fine.
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

test_script = """
    set list on;
    set term ^;
    create or alter package pg_test as
    begin
       -- empty! --
    end
    ^
    commit
    ^
    execute block as
    begin
        execute statement ('drop package body pg_test');
        execute statement ('drop package pg_test');
    end
    ^
    commit
    ^
    select rdb$get_context('USER_SESSION', 'NO_SUCH_VARIABLE') as "Value:" from rdb$database
    ^
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    Value: <null>
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
