#coding:utf-8

"""
ID:          issue-6166
ISSUE:       6166
TITLE:       Enhance dynamic libraries loading related error messages
DESCRIPTION:
    We intentionally try to load unit from non-existent UDR module with name "udrcpp_foo".
    Message 'module not found' issued BEFORE fix - without any detailization.
    Current output should contain phrase: 'UDR module not loaded'.
    Filtering is used for prevent output of localized message about missed UDR library.
JIRA:        CORE-5908
FBTEST:      bugs.core_5908
NOTES:
    [23.04.2026] pzotov
    Added substitutions to ignore presense or absense of leading dash ('-') at line with error message.
    Checked on 6.0.0.1914; 5.0.5.1817; 4.0.7.3271; 3.0.14.33855.
"""

import pytest
import re
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()

act = python_act('db', substitutions = [('^(-)?', '')])

expected_stdout = """
    UDR module not loaded
"""

@pytest.mark.version('>=3.0.4')
def test_1(act: Action, capsys):
    udr_ddl = """
    create or alter procedure gen_foo2 (
        start_n integer not null,
        end_n integer not null
    ) returns( n integer not null )
        external name 'udrcpp_foo!gen_rows'
        engine udr
    """
    pattern = re.compile('\\.*module\\s+not\\s+(found|loaded)\\.*', re.IGNORECASE)
    with act.db.connect() as con:
        try:
            con.execute_immediate(udr_ddl)
            con.commit()
        except DatabaseError as e:
            for line in str(e).splitlines():
                if pattern.search(line):
                    print(line)
    # Check
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
