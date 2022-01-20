#coding:utf-8

"""
ID:          issue-1735
ISSUE:       1735
TITLE:       NOT NULL constraint for procedure parameters and variables
DESCRIPTION:
JIRA:        CORE-1316
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """create procedure get_something(id integer not null) as begin end;
commit;
execute procedure get_something(NULL);
execute procedure get_something(1);
set term ^;
create procedure p0(inp int) as declare i int not null; begin i = inp; end^
set term ;^
commit;
execute procedure p0(null);
execute procedure p0(1);
"""

act = isql_act('db', test_script, substitutions=[('line: \\d+, col: \\d+', '')])

expected_stderr = """Statement failed, SQLSTATE = 42000
validation error for variable ID, value "*** null ***"
-At procedure 'GET_SOMETHING'
Statement failed, SQLSTATE = 42000
validation error for variable I, value "*** null ***"
-At procedure 'P0' line: 1, col: 63
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

