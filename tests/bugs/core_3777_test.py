#coding:utf-8
#
# id:           bugs.core_3777
# title:        Conversion error from string when using GROUP BY
# decription:   
# tracker_id:   CORE-3777
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TABLE2 (
    ID INTEGER NOT NULL,
    NAME VARCHAR(50)
);
ALTER TABLE TABLE2 ADD CONSTRAINT PK_TABLE2 PRIMARY KEY (ID);
COMMIT;
CREATE TABLE TABLE1 (
    ID INTEGER NOT NULL,
    ID_NAME INTEGER,
    NAME COMPUTED BY (COALESCE((SELECT NAME FROM TABLE2 WHERE ID = ID_NAME) || '.', '')),
    OTHER_FIELD INTEGER
);
ALTER TABLE TABLE1 ADD CONSTRAINT PK_TABLE1 PRIMARY KEY (ID);
COMMIT;
INSERT INTO TABLE2 (ID, NAME) VALUES (1, 'qqq');
INSERT INTO TABLE2 (ID, NAME) VALUES (2, 'www');
INSERT INTO TABLE2 (ID, NAME) VALUES (3, 'eee');
COMMIT;
INSERT INTO TABLE1 (ID, ID_NAME, OTHER_FIELD) VALUES (1, 1, 100);
INSERT INTO TABLE1 (ID, ID_NAME, OTHER_FIELD) VALUES (2, 2, 101);
INSERT INTO TABLE1 (ID, ID_NAME, OTHER_FIELD) VALUES (3, 3, 102);
COMMIT;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT T.NAME FROM TABLE1 T GROUP BY T.NAME,T.OTHER_FIELD;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """SQL>
NAME
===================================================
eee.
qqq.
www.

SQL>"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

