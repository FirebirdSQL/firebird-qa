#coding:utf-8

"""
ID:          issue-3808
ISSUE:       3808
TITLE:       Collation is not installed with icu > 4.2
DESCRIPTION:
JIRA:        CORE-3447
FBTEST:      bugs.core_3447
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(
        name1 varchar(32) character set utf8 collate ucs_basic,
        name2 varchar(32) character set utf8 collate unicode,
        name3 varchar(32) character set utf8 collate unicode_ci,
        name4 varchar(32) character set utf8 collate unicode_ci_ai
    );
    commit;
    show table test;
    -- Passed on: WI-V2.5.5.26871, WI-T3.0.0.31844; LI-V2.5.3.26788, LI-T3.0.0.31842
"""

act = isql_act('db', test_script)

expected_stdout = """
    NAME1                           VARCHAR(32) CHARACTER SET UTF8 Nullable
                                     COLLATE UCS_BASIC
    NAME2                           VARCHAR(32) CHARACTER SET UTF8 Nullable
                                     COLLATE UNICODE
    NAME3                           VARCHAR(32) CHARACTER SET UTF8 Nullable
                                     COLLATE UNICODE_CI
    NAME4                           VARCHAR(32) CHARACTER SET UTF8 Nullable
                                     COLLATE UNICODE_CI_AI
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

