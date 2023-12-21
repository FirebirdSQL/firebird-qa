#coding:utf-8

"""
ID:          issue-5231
ISSUE:       5231
TITLE:       Add label about deterministic flag for stored function in SHOW and extract commands
DESCRIPTION:
JIRA:        CORE-4940
FBTEST:      bugs.core_4940
NOTES:
    [12.12.2023] pzotov
    Added 'SQLSTATE' in substitutions: runtime error must not be filtered out by '?!(...)' pattern
    ("negative lookahead assertion", see https://docs.python.org/3/library/re.html#regular-expression-syntax).
    Added 'combine_output = True' in order to see SQLSTATE if any error occurs.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- 1. Specify 'deterministic' flag - it should be reflected in SHOW command:
    set term ^;
    create or alter function fn_infinity returns bigint deterministic as
    begin
        return 9223372036854775807;
    end
    ^
    set term ;^
    commit;

    show function fn_infinity;

    -- 2. Remove 'deterministic' flag - it also should be reflected in SHOW command:
    set term ^;
    alter function fn_infinity returns bigint as
    begin
        return 9223372036854775807;
    end
    ^
    set term ;^
    commit;

    show function fn_infinity;
"""

act = isql_act('db', test_script, substitutions=[('^((?!SQLSTATE|[Ff]unction|[Dd]eterministic).)*$', '')])

expected_stdout = """
    Deterministic function
    Function text:

    Function text:
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

