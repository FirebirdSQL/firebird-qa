#coding:utf-8
#
# id:           bugs.core_2073
# title:        Expression indexes bug: incorrect result for the inverted boolean
# decription:   
# tracker_id:   CORE-2073
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_2073

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TMP_DATE1
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT count(*) FROM TMP_DATE1 T WHERE '01.03.2008' BETWEEN T.DATE1+0 AND T.DATE2;
SELECT count(*) FROM TMP_DATE1 T  WHERE '01.03.2008' >= T.DATE1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

