#coding:utf-8

"""
ID:          issue-7482
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7482
TITLE:       Result of blob_append(null, null) (literal '<null>') is not shown
NOTES:
    [14.02.2023] pzotov
    Checked on 5.0.0.958, intermediate build of 24-feb-2023. All OK.

    [03.03.2023] pzotov
    Waiting for patch in FB 4.x that fixes problem with <null> literal (4.0.3.2904 still fails).
    Added substitution for suppressing 'Nullable' flags in the SQLDA output: it is sufficient for this test
    to check only datatypes of result.
    Discussed with Vlad, letters 02-mar-2023 16:01 and 03-mar-2023 14:43.
    Checked on 5.0.0.967.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set blob all;
    set sqlda_display on;
    select blob_append(null, null) as blob_result from rdb$database;
"""

act = isql_act('db', test_script, substitutions = [('^((?!sqltype:|BLOB_RESULT).)*$', ''), ('BLOB Nullable', 'BLOB'), ('[ \t]+', ' ')])

expected_stdout = """
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 0 len: 8
    :  name: BLOB_APPEND  alias: BLOB_RESULT
    BLOB_RESULT              <null>
"""

@pytest.mark.version('>=5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
