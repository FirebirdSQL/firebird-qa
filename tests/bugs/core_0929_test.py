#coding:utf-8
#
# id:           bugs.core_0929
# title:        Bug in DSQL parameter
# decription:
# tracker_id:   CORE-929
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_929

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST (MYDATE DATE NOT NULL PRIMARY KEY);
COMMIT;

INSERT INTO TEST VALUES (CURRENT_DATE);
INSERT INTO TEST VALUES (CURRENT_DATE + 1);
INSERT INTO TEST VALUES (CURRENT_DATE + 2);
INSERT INTO TEST VALUES (CURRENT_DATE + 3);
COMMIT;

"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  try:
#    c.prep('SELECT * FROM TEST WHERE MYDATE + CAST(? AS INTEGER) >= ?')
#  except Exception,e:
#    print ('Test FAILED')
#    print (e)
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    with act_1.db.connect() as con:
        c = con.cursor()
        try:
            c.prepare('SELECT * FROM TEST WHERE MYDATE + CAST(? AS INTEGER) >= ?')
        except:
            pytest.fail("Test FAILED")


