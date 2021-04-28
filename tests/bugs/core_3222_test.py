#coding:utf-8
#
# id:           bugs.core_3222
# title:        View with "WITH CHECK OPTION" doesn't like TRIM function in WHERE
# decription:   
# tracker_id:   CORE-3222
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Foo (
  Bar INTEGER,
  Str CHAR(31)
);
COMMIT;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE VIEW VIEW_Foo (
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_3222.fdb, User: SYSDBA
SQL> CON> CON> CON> CON> CON> CON> CON> SQL> SQL> BAR                             INTEGER Nullable
View Source:
==== ======
 SELECT
     Bar
  FROM Foo
  WHERE(Trim(Str) = 'test')
WITH CHECK OPTION
SQL>"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

