#coding:utf-8

"""
ID:          issue-3313
ISSUE:       3313
TITLE:       DROP VIEW drops output parameters of used stored procedures
DESCRIPTION:
JIRA:        CORE-2930
"""

import pytest
from firebird.qa import *

init_script = """set term !;
create procedure p1 returns (n integer) as begin suspend; end!
create view v1 as select * from p1!
commit!
set term ;!
"""

db = db_factory(charset='UTF8', init=init_script)

test_script = """show procedure p1;
drop view v1;
show procedure p1;
"""

act = isql_act('db', test_script)

expected_stdout = """Procedure text:
=============================================================================
 begin suspend; end
=============================================================================
Parameters:
N                                 OUTPUT INTEGER
Procedure text:
=============================================================================
 begin suspend; end
=============================================================================
Parameters:
N                                 OUTPUT INTEGER
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

