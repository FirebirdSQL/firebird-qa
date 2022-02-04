#coding:utf-8

"""
ID:          domain.create-43
FBTEST:      functional.domain.create.54
ISSUE:       1026
JIRA:        CORE-660
TITLE:       Use of domains for Trigger/SP variable definition
DESCRIPTION:
  Allow domains to be applied to variables and in/out parameters within a trigger or SP
"""

import pytest
from firebird.qa import *

db = db_factory(init="create domain d as integer;")

test_script = """set term !!;
create procedure sp (i type of d) returns (o type of d)
as
  declare variable v type of d;
begin
  v = cast(v as type of d);
end!!
commit!!
set term ;!!
show procedure sp;"""

act = isql_act('db', test_script)

expected_stdout = """Procedure text:
=============================================================================
  declare variable v type of d;
begin
  v = cast(v as type of d);
end
=============================================================================
Parameters:
I                                 INPUT (TYPE OF D) INTEGER
O                                 OUTPUT (TYPE OF D) INTEGER"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
