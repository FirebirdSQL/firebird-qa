#coding:utf-8

"""
ID:          issue-2926
ISSUE:       2926
TITLE:       Wrong processing a SP parameters with arrays
DESCRIPTION:
JIRA:        CORE-2516
"""

import pytest
from firebird.qa import *

init_script = """
    create domain t_smallint_array as smallint [0:2];
"""

db = db_factory(init=init_script)

test_script = """
    set term ^;
    create procedure sp_smallint_array(x t_smallint_array)
     returns (y t_smallint_array)
    as
    begin
      y=x;
      suspend;
    end
    ^ set term ;^
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 0A000
    CREATE PROCEDURE SP_SMALLINT_ARRAY failed
    -Dynamic SQL Error
    -feature is not supported
    -Usage of domain or TYPE OF COLUMN of array type in PSQL
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

