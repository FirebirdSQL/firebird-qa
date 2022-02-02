#coding:utf-8

"""
ID:          issue-5613
ISSUE:       5613
TITLE:       Regression: The subquery in the insert list expressions ignore the changes
  made earlier in the same executable block.
DESCRIPTION:
JIRA:        CORE-5337
FBTEST:      bugs.core_5337
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test (
        id integer not null,
        val integer not null
    );

    set term ^;
    execute block
    as
    begin
      insert into test (id, val) values (1, 100);
      insert into test (id, val) values (2, (select val from test where id = 1));
    end
    ^
    set term ;^

    set list on;
    select * from test;
    rollback;
"""

act = isql_act('db', test_script)

expected_stdout = """
    ID                              1
    VAL                             100

    ID                              2
    VAL                             100
"""

@pytest.mark.version('>=3.0.1')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

