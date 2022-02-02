#coding:utf-8

"""
ID:          issue-3913
ISSUE:       3913
TITLE:       AV in engine when preparing query against dropping table
DESCRIPTION:
JIRA:        CORE-3557
FBTEST:      bugs.core_3557
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='core3557.fbk')

test_script = """
    -- Confirmed for 2.5.0 only: server crashes on running the following EB. 26.02.2015
    -- All subsequent releases should produce no stdout & stderr.
    set term ^;
    execute block as
    begin
      execute statement 'drop table t';
      in autonomous transaction do
        execute statement ('insert into t values (1)');
    end ^
"""

act = isql_act('db', test_script)

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.execute()
