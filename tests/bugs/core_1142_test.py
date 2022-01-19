#coding:utf-8

"""
ID:          issue-1564
ISSUE:       1564
TITLE:       Cannot alter generator's comment to the same value
DESCRIPTION:
JIRA:        CORE-1142
"""

import pytest
from firebird.qa import *

init_script = """create generator T;"""

db = db_factory(init=init_script)

test_script = """comment on generator T is 'comment';
commit;
show comment on generator T;
comment on generator T is 'comment';
commit;
show comment on generator T;
comment on generator T is 'different comment';
commit;
show comment on generator T;
"""

act = isql_act('db', test_script)

expected_stdout = """COMMENT ON GENERATOR    T IS comment;
COMMENT ON GENERATOR    T IS comment;
COMMENT ON GENERATOR    T IS different comment;
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

