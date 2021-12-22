#coding:utf-8
#
# id:           bugs.core_202
# title:        ORDER BY works wrong with collate PT_PT
# decription:   
# tracker_id:   CORE-202
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_202

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE STOCKS (
    MNEN    INTEGER NOT NULL,
    ACTIVO  VARCHAR(50) CHARACTER SET ISO8859_1 COLLATE PT_PT
);

COMMIT WORK;

INSERT INTO STOCKS (MNEN, ACTIVO) VALUES (1, 'B&A');
INSERT INTO STOCKS (MNEN, ACTIVO) VALUES (2, 'BES');
INSERT INTO STOCKS (MNEN, ACTIVO) VALUES (3, 'BCP');
INSERT INTO STOCKS (MNEN, ACTIVO) VALUES (4, 'B&A Pref.');
INSERT INTO STOCKS (MNEN, ACTIVO) VALUES (5, 'Banif');

COMMIT WORK;

CREATE COLLATION PT_PT2 FOR ISO8859_1 FROM PT_PT 'SPECIALS-FIRST=1';

COMMIT WORK;

CREATE TABLE STOCKS2 (
    MNEN    INTEGER NOT NULL,
    ACTIVO  VARCHAR(50) CHARACTER SET ISO8859_1 COLLATE PT_PT2
);

COMMIT WORK;

INSERT INTO STOCKS2 (MNEN, ACTIVO) VALUES (1, 'B&A');
INSERT INTO STOCKS2 (MNEN, ACTIVO) VALUES (2, 'BES');
INSERT INTO STOCKS2 (MNEN, ACTIVO) VALUES (3, 'BCP');
INSERT INTO STOCKS2 (MNEN, ACTIVO) VALUES (4, 'B&A Pref.');
INSERT INTO STOCKS2 (MNEN, ACTIVO) VALUES (5, 'Banif');

COMMIT WORK;

"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT ACTIVO FROM STOCKS ORDER BY ACTIVO;

SELECT ACTIVO FROM STOCKS2 ORDER BY ACTIVO;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ACTIVO
==================================================
B&A
Banif
B&A Pref.
BCP
BES

ACTIVO
==================================================
B&A
B&A Pref.
Banif
BCP
BES

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

