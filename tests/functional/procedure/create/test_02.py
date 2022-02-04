#coding:utf-8

"""
ID:          procedure.create-02
TITLE:       CREATE PROCEDURE - Input parameters
DESCRIPTION:
FBTEST:      functional.procedure.create.02
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET TERM ^;
CREATE PROCEDURE test(
  p1 SMALLINT, p2 INTEGER, p3 FLOAT, p4 DOUBLE PRECISION, p5 DECIMAL(9,3), p6 NUMERIC(10,4),
  p7 DATE, p8 TIME, p9 TIMESTAMP, p10 CHAR(40), p11 VARCHAR(60), p12 NCHAR(70))
AS
BEGIN
  POST_EVENT 'Test';
END ^
SET TERM ;^
commit;
SHOW PROCEDURE test;"""

act = isql_act('db', test_script)

expected_stdout = """Procedure text:
=============================================================================
BEGIN
  POST_EVENT 'Test';
END
=============================================================================
Parameters:
P1                                INPUT SMALLINT
P2                                INPUT INTEGER
P3                                INPUT FLOAT
P4                                INPUT DOUBLE PRECISION
P5                                INPUT DECIMAL(9, 3)
P6                                INPUT NUMERIC(10, 4)
P7                                INPUT DATE
P8                                INPUT TIME
P9                                INPUT TIMESTAMP
P10                               INPUT CHAR(40)
P11                               INPUT VARCHAR(60)
P12                               INPUT CHAR(70) CHARACTER SET ISO8859_1"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
