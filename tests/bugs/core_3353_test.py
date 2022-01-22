#coding:utf-8

"""
ID:          issue-3719
ISSUE:       3719
TITLE:       Predicate (blob_field LIKE ?) describes the parameter as VARCHAR(30) rather than as BLOB
DESCRIPTION:
JIRA:        CORE-3353
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set sqlda_display on;
    set planonly;
    select rdb$procedure_source from rdb$procedures where rdb$procedure_source like ?;
    -- NB: output in 3.0 will contain values of sqltype with ZERO in bit_0,
    -- so it will be: 520 instead of previous 521.
    -- (see also: core_4156.fbt)
"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')])

# version: 3.0

expected_stdout_1 = """
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_1
    act.execute(charset='utf8')
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

expected_stdout_2 = """
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
"""

@pytest.mark.version('>=4.0')
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

