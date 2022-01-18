#coding:utf-8

"""
ID:          issue-613
ISSUE:       613
TITLE:       DOMAINs don't register their dependency on other objects
DESCRIPTION:
JIRA:        CORE-282
"""

import pytest
from firebird.qa import *

init_script = """create table t(a int);
create domain d int check(value > (select max(a) from t));
commit;"""

db = db_factory(init=init_script)

test_script = """drop table t;
commit;
create table u(a d);
commit;
show table u;
"""

act = isql_act('db', test_script)

expected_stdout = """A                               (D) INTEGER Nullable
                                check(value > (select max(a) from t))
"""
expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-COLUMN T.A
-there are 1 dependencies
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

