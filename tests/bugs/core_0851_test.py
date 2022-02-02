#coding:utf-8

"""
ID:          issue-1240
ISSUE:       1240
TITLE:       Field can be used multiple times in multi-segment index definition
DESCRIPTION:
JIRA:        CORE-851
FBTEST:      bugs.core_0851
"""

import pytest
from firebird.qa import *

init_script = """create table t (i integer);
commit;
"""

db = db_factory(init=init_script)

test_script = """create index ti on t(i,i);
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE INDEX TI failed
-Field I cannot be used twice in index TI
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

