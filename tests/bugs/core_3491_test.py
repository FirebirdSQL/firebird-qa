#coding:utf-8

"""
ID:          issue-3850
ISSUE:       3850
TITLE:       Altering of a TYPE OF COLUMN parameter affects the original column
DESCRIPTION:
JIRA:        CORE-3491
FBTEST:      bugs.core_3491
"""

import pytest
from firebird.qa import *

init_script = """create table aaa (a integer);
commit;
set term !!;
create or alter procedure bbb
returns (b type of column aaa.a)
as
begin
 suspend;
end!!
set term ;!!
commit;
"""

db = db_factory(init=init_script)

test_script = """show table aaa;
set term !!;
create or alter procedure bbb
returns (b varchar(10))
as
begin
 suspend;
end!!
set term ;!!
commit;
show table aaa;
"""

act = isql_act('db', test_script)

expected_stdout = """A                               INTEGER Nullable
A                               INTEGER Nullable
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

