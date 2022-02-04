#coding:utf-8

"""
ID:          procedure.create-04
TITLE:       CREATE PROCEDURE - Output paramaters
DESCRIPTION:
FBTEST:      functional.procedure.create.04
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET TERM ^;
CREATE PROCEDURE test
AS
DECLARE VARIABLE p1 SMALLINT;
DECLARE VARIABLE p2 INTEGER;
DECLARE VARIABLE p3 FLOAT;
DECLARE VARIABLE p4 DOUBLE PRECISION;
DECLARE VARIABLE p5 DECIMAL(9,3);
DECLARE VARIABLE p6 NUMERIC(10,4);
DECLARE VARIABLE p7 DATE;
DECLARE VARIABLE p8 TIME;
DECLARE VARIABLE p9 TIMESTAMP;
DECLARE VARIABLE p10 CHAR(40);
DECLARE VARIABLE p11 VARCHAR(60);
DECLARE VARIABLE p12 NCHAR(70);
BEGIN
  p1=1;
  p2=2;
  p3=3.4;
  p4=4.5;
  p5=5.6;
  p6=6.7;
  p7='31.8.1995';
  p8='13:45:57.1';
  p9='29.2.200 14:46:59.9';
  p10='Text p10';
  p11='Text p11';
  p12='Text p13';
END ^
SET TERM ;^
commit;
SHOW PROCEDURE test;"""

act = isql_act('db', test_script)

expected_stdout = """Procedure text:
=============================================================================
DECLARE VARIABLE p1 SMALLINT;
DECLARE VARIABLE p2 INTEGER;
DECLARE VARIABLE p3 FLOAT;
DECLARE VARIABLE p4 DOUBLE PRECISION;
DECLARE VARIABLE p5 DECIMAL(9,3);
DECLARE VARIABLE p6 NUMERIC(10,4);
DECLARE VARIABLE p7 DATE;
DECLARE VARIABLE p8 TIME;
DECLARE VARIABLE p9 TIMESTAMP;
DECLARE VARIABLE p10 CHAR(40);
DECLARE VARIABLE p11 VARCHAR(60);
DECLARE VARIABLE p12 NCHAR(70);
BEGIN
  p1=1;
  p2=2;
  p3=3.4;
  p4=4.5;
  p5=5.6;
  p6=6.7;
  p7='31.8.1995';
  p8='13:45:57.1';
  p9='29.2.200 14:46:59.9';
  p10='Text p10';
  p11='Text p11';
  p12='Text p13';
END
============================================================================="""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
