#coding:utf-8

"""
ID:          issue-1239
ISSUE:       1239
TITLE:       DateTime math imprecision
DESCRIPTION:
JIRA:        CORE-850
"""

import pytest
from firebird.qa import *

init_script = """create table t2(a int, b int computed by (00));
commit;
"""

db = db_factory(init=init_script)

test_script = """alter table t2 alter b set default 5;
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER TABLE T2 failed
-Cannot add or remove COMPUTED from column B
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

