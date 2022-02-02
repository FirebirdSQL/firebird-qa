#coding:utf-8

"""
ID:          issue-4105
ISSUE:       4105
TITLE:       Conversion error when using a blob as an argument for the EXCEPTION statement
DESCRIPTION:
JIRA:        CORE-3761
FBTEST:      bugs.core_3761
"""

import pytest
from firebird.qa import *

init_script = """
    CREATE EXCEPTION CHECK_EXCEPTION 'Check exception';
    COMMIT;
"""

db = db_factory(init=init_script)

test_script = """
    SET TERM ^;
    EXECUTE BLOCK AS
    BEGIN
        EXCEPTION CHECK_EXCEPTION CAST ('WORD' AS BLOB SUB_TYPE TEXT);
    END^^
    SET TERM ;^
"""

act = isql_act('db', test_script, substitutions=[('-At block line: [\\d]+, col: [\\d]+', '-At block line')])

expected_stderr = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -CHECK_EXCEPTION
    -WORD
    -At block line: 4, col: 2
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

