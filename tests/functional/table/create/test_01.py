#coding:utf-8

"""
ID:          table.create-01
TITLE:       CREATE TABLE - types
DESCRIPTION:
FBTEST:      functional.table.create.01
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE TABLE test(
 c1 SMALLINT,
 c2 INTEGER,
 c3 FLOAT,
 c4 DOUBLE PRECISION,
 c5 DATE,
 c6 TIME,
 c7 TIMESTAMP,
 c8 DECIMAL(18,4),
 c9 NUMERIC(1,1),
 c10 CHAR(800),
 c11 CHARACTER(9000),
 c12 CHARACTER VARYING(1600),
 c13 VARCHAR(12000),
 c14 NCHAR (12),
 c15 NATIONAL CHARACTER(20),
 c16 NATIONAL CHAR(200),
 c17 NCHAR VARYING(1600),
 c18 NATIONAL CHARACTER VARYING(16000),
 c19 NATIONAL CHAR VARYING(16000),
 c20 BLOB,
 c21 BLOB SUB_TYPE 1,
 c22 BLOB SEGMENT SIZE 512,
 c23 BLOB (1024,1)
);
SHOW TABLE test;
"""

act = isql_act('db', test_script)

expected_stdout = """C1                              SMALLINT Nullable
C2                              INTEGER Nullable
C3                              FLOAT Nullable
C4                              DOUBLE PRECISION Nullable
C5                              DATE Nullable
C6                              TIME Nullable
C7                              TIMESTAMP Nullable
C8                              DECIMAL(18, 4) Nullable
C9                              NUMERIC(1, 1) Nullable
C10                             CHAR(800) Nullable
C11                             CHAR(9000) Nullable
C12                             VARCHAR(1600) Nullable
C13                             VARCHAR(12000) Nullable
C14                             CHAR(12) CHARACTER SET ISO8859_1 Nullable
C15                             CHAR(20) CHARACTER SET ISO8859_1 Nullable
C16                             CHAR(200) CHARACTER SET ISO8859_1 Nullable
C17                             VARCHAR(1600) CHARACTER SET ISO8859_1 Nullable
C18                             VARCHAR(16000) CHARACTER SET ISO8859_1 Nullable
C19                             VARCHAR(16000) CHARACTER SET ISO8859_1 Nullable
C20                             BLOB segment 80, subtype BINARY Nullable
C21                             BLOB segment 80, subtype TEXT Nullable
C22                             BLOB segment 512, subtype BINARY Nullable
C23                             BLOB segment 1024, subtype TEXT Nullable
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
