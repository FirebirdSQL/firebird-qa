#coding:utf-8

"""
ID:          issue-2322
ISSUE:       2322
TITLE:       SHOW VIEW shows non-sense information for view fields with expressions
DESCRIPTION:
JIRA:        CORE-1891
FBTEST:      bugs.core_1891
"""

import pytest
from firebird.qa import *

init_script = """create table test (n integer);
create view view_test (x, y) as select n, n * 2 from test;
"""

db = db_factory(init=init_script)

test_script = """show view view_test;
"""

act = isql_act('db', test_script)

expected_stdout = """X                               INTEGER Nullable
Y                               BIGINT Expression
View Source:
==== ======
 select n, n * 2 from test
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

