#coding:utf-8

"""
ID:          issue-1479
ISSUE:       1479
TITLE:       ALTER DOMAIN and ALTER TABLE don't allow to change character set and/or collation
DESCRIPTION:
JIRA:        CORE-1058
FBTEST:      bugs.core_1058
"""

import pytest
from firebird.qa import *

init_script = """CREATE DOMAIN D_TEST AS VARCHAR(100) CHARACTER SET WIN1251;
COMMIT;
"""

db = db_factory(init=init_script)

test_script = """ALTER DOMAIN D_TEST TYPE VARCHAR(100) CHARACTER SET UTF8;
COMMIT;
SHOW DOMAIN D_TEST;
"""

act = isql_act('db', test_script)

expected_stdout = """D_TEST                          VARCHAR(100) CHARACTER SET UTF8 Nullable
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

