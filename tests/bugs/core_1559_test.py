#coding:utf-8

"""
ID:          issue-1978
ISSUE:       1978
TITLE:       Dropping NOT NULL contranint doesn'have the desired effect
DESCRIPTION:
JIRA:        CORE-1559
FBTEST:      bugs.core_1559
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """create table t (n integer constraint c not null);
COMMIT;
insert into t values (null);
COMMIT;
alter table t drop constraint c;
COMMIT;
insert into t values (null);
COMMIT;
SELECT * FROM t;
"""

act = isql_act('db', test_script)

expected_stdout = """
           N
============
      <null>

"""

expected_stderr = """Statement failed, SQLSTATE = 23000
validation error for column "T"."N", value "*** null ***"
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

