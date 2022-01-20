#coding:utf-8

"""
ID:          issue-19285
ISSUE:       19285
TITLE:       Bad XSQLVAR [NULL flags] for (2*COALESCE(NULL,NULL))
DESCRIPTION:
JIRA:        CORE-1510
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set sqlda_display;
    select 2*COALESCE(NULL,NULL) from RDB$DATABASE;
    select 2*IIF(NULL is NULL, NULL, NULL) from RDB$DATABASE;
"""

act = isql_act('db', test_script,
                 substitutions=[('^((?!sqltype).)*$', ''), ('[ ]+', ' '),
                                ('[\t]*', ' '), ('charset:.*', '')])

expected_stdout = """
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

