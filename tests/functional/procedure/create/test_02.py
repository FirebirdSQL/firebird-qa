#coding:utf-8
#
# id:           functional.procedure.create.02
# title:        CREATE PROCEDURE - Input parameters
# decription:   CREATE PROCEDURE - Input parameters
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.procedure.create.create_procedure_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Procedure text:
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

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

