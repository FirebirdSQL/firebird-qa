#coding:utf-8

"""
ID:          issue-4402
ISSUE:       4402
TITLE:       Computed by columns and position function
DESCRIPTION:
JIRA:        CORE-4074
FBTEST:      bugs.core_4074
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table test01 (
      f01 computed by ( 'fabio ' || position('x','schunig') ),
      f02 numeric(8,2) default 0
    );
"""

db = db_factory(init=init_script)

test_script = """
    show table test01;
    -- ::: NB ::: On WI-V2.5.4.26856, 26-mar-2015, output is:
    -- F01                             Computed by: ( 'fabio ' || position('x','schunig') ),
    --   f02 numeric(8,2) default 0
    -- )
    -- F02                             NUMERIC(8, 2) Nullable )
    -- (i.e. it DOES contain "strange" last line)
"""

act = isql_act('db', test_script)

expected_stdout = """
    F01                             Computed by: ( 'fabio ' || position('x','schunig') )
    F02                             NUMERIC(8, 2) Nullable default 0
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

