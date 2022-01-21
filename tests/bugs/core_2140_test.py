#coding:utf-8

"""
ID:          issue-2571
ISSUE:       2571
TITLE:       Error messages after parameters substitution contains '\\n' characters instead of line break
DESCRIPTION:
JIRA:        CORE-2140
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set term ^ ;
    execute block returns (y int) as
    begin
      for execute statement
          ('select rdb$relation_id from rdb$database where rdb$relation_id = :x') (1)
        with autonomous transaction
        into y
      do suspend;
    end ^
"""

act = isql_act('db', test_script,
                 substitutions=[('column.*', 'column x'),
                                ('-At block line: [\\d]+, col: [\\d]+', '')])

expected_stderr = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -X
    -At line 1, column 67
    -At block line: 5, col: 3
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

