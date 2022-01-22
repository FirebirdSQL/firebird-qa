#coding:utf-8

"""
ID:          issue-3596
ISSUE:       3596
TITLE:       View with "WITH CHECK OPTION" doesn't like TRIM function in WHERE
DESCRIPTION:
JIRA:        CORE-3222
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Foo (
  Bar INTEGER,
  Str CHAR(31)
);
COMMIT;
"""

db = db_factory(init=init_script)

test_script = """CREATE VIEW VIEW_Foo (
     Bar
) AS SELECT
     Bar
  FROM Foo
  WHERE(Trim(Str) = 'test')
WITH CHECK OPTION
;
COMMIT;
SHOW VIEW VIEW_Foo;
"""

act = isql_act('db', test_script)

expected_stdout = """BAR                             INTEGER Nullable
View Source:
==== ======
 SELECT
     Bar
  FROM Foo
  WHERE(Trim(Str) = 'test')
WITH CHECK OPTION
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

