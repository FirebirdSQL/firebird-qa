#coding:utf-8
#
# id:           bugs.core_1306
# title:        Indices not used for views
# decription:   
# tracker_id:   CORE-1306
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1306

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE "TABLE" (ID INTEGER NOT NULL PRIMARY KEY);

COMMIT;

INSERT INTO "TABLE" (ID) VALUES (1);
INSERT INTO "TABLE" (ID) VALUES (2);
INSERT INTO "TABLE" (ID) VALUES (3);

COMMIT;

CREATE VIEW "VIEW" AS SELECT * FROM "TABLE";

commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set plan on;

SELECT * FROM "TABLE" WHERE ID = 1
UNION ALL
SELECT * FROM "VIEW" WHERE ID = 1 ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN (TABLE INDEX (RDB$PRIMARY1), VIEW TABLE INDEX (RDB$PRIMARY1))

          ID
============
           1
           1

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

