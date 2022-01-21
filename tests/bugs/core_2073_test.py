#coding:utf-8

"""
ID:          issue-2508
ISSUE:       2508
TITLE:       Expression indexes bug: incorrect result for the inverted boolean
DESCRIPTION:
JIRA:        CORE-1000
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE TMP_DATE1
(
  DATE1 DATE,
  DATE2 DATE
);
COMMIT;
SET TERM !!;
EXECUTE BLOCK
AS
  DECLARE VARIABLE D DATE;
BEGIN
  D = '01.01.2008';
  WHILE (D < '01.08.2008') DO BEGIN
    INSERT INTO TMP_DATE1(DATE1, DATE2)
      VALUES(:D, :D + 100);
      D = D + 1;
  END
END!!
SET TERM ;!!
COMMIT;
CREATE INDEX TMP_DATE1_IDX1 ON TMP_DATE1 COMPUTED BY (DATE1+0);
CREATE INDEX TMP_DATE1_IDX2 ON TMP_DATE1 (DATE1);
COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT count(*) FROM TMP_DATE1 T WHERE '01.03.2008' BETWEEN T.DATE1+0 AND T.DATE2;
SELECT count(*) FROM TMP_DATE1 T  WHERE '01.03.2008' >= T.DATE1;
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (T INDEX (TMP_DATE1_IDX1))

                COUNT
=====================
                   61


PLAN (T INDEX (TMP_DATE1_IDX2))

                COUNT
=====================
                   61

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

