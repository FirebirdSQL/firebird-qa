#coding:utf-8

"""
ID:          issue-4105
ISSUE:       4105
TITLE:       Conversion error when using a blob as an argument for the EXCEPTION statement
DESCRIPTION:
JIRA:        CORE-3761
FBTEST:      bugs.core_3761
NOTES:
    [25.11.2023] pzotov
    Writing code requires more care since 6.0.0.150: ISQL does not allow specifying duplicate delimiters without any statements between them (two semicolon, two carets etc).
"""

import pytest
from firebird.qa import *

init_script = """
    create exception check_exception 'check exception';
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set term ^;
    execute block as
    begin
        exception check_exception cast ('word' as blob sub_type text);
    end^
    set term ;^
"""

act = isql_act('db', test_script, substitutions=[('-At block line: [\\d]+, col: [\\d]+', '-At block line')])

expected_stdout = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -CHECK_EXCEPTION
    -word
    -At block line: 4, col: 2
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

