#coding:utf-8

"""
ID:          issue-428
ISSUE:       428
TITLE:       Dropping and recreating a table in the same txn disables PK
DESCRIPTION:
JIRA:        CORE-104
FBTEST:      bugs.core_0104
"""

import pytest
from firebird.qa import *

init_script = """create table test (acolumn int not null primary key);
commit;
"""

db = db_factory(init=init_script)

test_script = """SET AUTODDL OFF;

drop table test;
create table test (acolumn int not null primary key);

commit;

insert into test values (1);
insert into test values (1);

commit;
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "INTEG_4" on table "TEST"
-Problematic key value is ("ACOLUMN" = 1)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

