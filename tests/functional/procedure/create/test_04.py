#coding:utf-8
#
# id:           functional.procedure.create.04
# title:        CREATE PROCEDURE - Output paramaters
# decription:   CREATE PROCEDURE - Output paramaters
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.procedure.create.create_procedure_04

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
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
SHOW PROCEDURE test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Procedure text:
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
=============================================================================
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

