#coding:utf-8

"""
ID:          issue-3554
ISSUE:       3554
TITLE:       ALTER VIEW with not matched columns in declaration and selection crashs the server
DESCRIPTION:
JIRA:        CORE-3180
"""

import pytest
from firebird.qa import *

init_script = """create view TEST_VIEW (ID) as select 1 from rdb$database;
commit;"""

db = db_factory(init=init_script)

test_script = """alter view TEST_VIEW (ID) as select 1, 2 from rdb$database;
COMMIT;
SHOW VIEW TEST_VIEW;
"""

act = isql_act('db', test_script)

expected_stdout = """ID                              INTEGER Expression
View Source:
==== ======
 select 1 from rdb$database
"""

expected_stderr = """Statement failed, SQLSTATE = 07002
unsuccessful metadata update
-ALTER VIEW TEST_VIEW failed
-SQL error code = -607
-Invalid command
-number of columns does not match select list
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

