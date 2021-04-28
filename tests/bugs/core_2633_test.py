#coding:utf-8
#
# id:           bugs.core_2633
# title:        SELECT WITH LOCK with no fields are accessed clears the data
# decription:   
# tracker_id:   CORE-2633
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T (A VARCHAR(20), B INTEGER);
INSERT INTO T(A,B) VALUES('aaaa',1);
INSERT INTO T(A,B) VALUES('bbbb',2);
INSERT INTO T(A,B) VALUES('cccc',3);
COMMIT;
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT * FROM T;

SET TERM ^;
EXECUTE BLOCK AS
DECLARE I INTEGER;
BEGIN
  FOR SELECT 1 FROM T WITH LOCK INTO :I DO I=I;
END^
SET TERM ;^

SELECT * FROM T;

ROLLBACK;

SELECT * FROM T;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
A                               B
==================== ============
aaaa                            1
bbbb                            2
cccc                            3


A                               B
==================== ============
aaaa                            1
bbbb                            2
cccc                            3


A                               B
==================== ============
aaaa                            1
bbbb                            2
cccc                            3

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

