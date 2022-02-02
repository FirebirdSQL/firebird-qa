#coding:utf-8

"""
ID:          issue-1511
ISSUE:       1511
TITLE:       Error msg "Could not find UNIQUE INDEX" when in fact one is present
DESCRIPTION:
JIRA:        CORE-1090
FBTEST:      bugs.core_1090
"""

import pytest
from firebird.qa import *

init_script = """create table t (i integer not null);
create unique index ti on t(i);
commit;
"""

db = db_factory(init=init_script)

test_script = """show table t;
show index ti;

create table t2 (i integer references t(i));
"""

act = isql_act('db', test_script)

expected_stdout = """I                               INTEGER Not Null
TI UNIQUE INDEX ON T(I)
"""

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLE T2 failed
-could not find UNIQUE or PRIMARY KEY constraint in table T with specified columns
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

