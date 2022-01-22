#coding:utf-8

"""
ID:          issue-3550
ISSUE:       3550
TITLE:       View with "subselect" column join table and not use index
DESCRIPTION:
JIRA:        CORE-3176
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE TMP
(
  ID Integer NOT NULL,
  CONSTRAINT PK_TMP_1 PRIMARY KEY (ID)
);
COMMIT;
CREATE VIEW TMP_VIEW (ID1, ID2)
AS
SELECT 1,(SELECT 1 FROM RDB$DATABASE) FROM RDB$DATABASE;
COMMIT;"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT * FROM tmp_view TV LEFT JOIN tmp T ON T.id=TV.id2;
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (TV RDB$DATABASE NATURAL)
PLAN (TV RDB$DATABASE NATURAL)
PLAN JOIN (TV RDB$DATABASE NATURAL, T INDEX (PK_TMP_1))

         ID1          ID2           ID
============ ============ ============
           1            1       <null>
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

