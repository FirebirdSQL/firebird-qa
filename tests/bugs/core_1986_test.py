#coding:utf-8

"""
ID:          issue-2424
ISSUE:       2424
TITLE:       Altering domains name drops dependencies using the domain
DESCRIPTION:
JIRA:        CORE-1986
"""

import pytest
from firebird.qa import *

init_script = """CREATE DOMAIN D_SOME AS INTEGER;

CREATE OR ALTER PROCEDURE SP_SOME(
    SOME_PARAM D_SOME)
AS
BEGIN
END;
"""

db = db_factory(init=init_script)

test_script = """ALTER DOMAIN D_SOME TO D_OTHER;

execute procedure SP_SOME (1);
commit;
execute procedure SP_SOME (1);
commit;
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-DOMAIN D_SOME
-there are 1 dependencies
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

