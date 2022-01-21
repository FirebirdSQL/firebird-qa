#coding:utf-8

"""
ID:          issue-3130
ISSUE:       3130
TITLE:       isql hangs when trying to show a view based on a procedure
DESCRIPTION:
JIRA:        CORE-2735
"""

import pytest
from firebird.qa import *

init_script = """set term ^;
create procedure p returns(a int) as begin a = 9; suspend; end^
create view vp1 as select a from p^
set term ;^
COMMIT;"""

db = db_factory(charset='UTF8', init=init_script)

test_script = """show view vp1;
"""

act = isql_act('db', test_script)

expected_stdout = """A                               INTEGER Nullable
View Source:
==== ======
 select a from p
"""

@pytest.mark.version('>=2.5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

