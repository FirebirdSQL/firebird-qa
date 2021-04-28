#coding:utf-8
#
# id:           bugs.core_1215
# title:        Wrong SELECT query results using index to evaluate >= condition
# decription:   
# tracker_id:   CORE-1215
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1215

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T (ID INT);
COMMIT;

set term ^;

EXECUTE BLOCK AS
DECLARE I INT = 0;
BEGIN
  WHILE (I < 50000) DO
  BEGIN
    INSERT INTO T VALUES (1);
    I = I + 1;
  END
END^

set term ;^
commit;

CREATE INDEX IDX_T ON T (ID);
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set plan on;
SELECT COUNT(*) FROM T ;
SELECT COUNT(*) FROM T WHERE ID >= 1 ;
SELECT COUNT(*) FROM T WHERE ID = 1 ;
SELECT COUNT(*) FROM T WHERE ID <= 1 ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (T NATURAL)

                COUNT
=====================
                50000

PLAN (T INDEX (IDX_T))

                COUNT
=====================
                50000

PLAN (T INDEX (IDX_T))

                COUNT
=====================
                50000

PLAN (T INDEX (IDX_T))

                COUNT
=====================
                50000

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

