#coding:utf-8
#
# id:           functional.procedure.create.15
# title:        COLLATE IN STORED PROCEDURE
# decription:   
# tracker_id:   CORE-684
# min_versions: []
# versions:     2.1
# qmid:         functional.procedure.create.create_procedure_15

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM !!;
CREATE PROCEDURE NEW_PROCEDURE (NOM1 VARCHAR(20) CHARACTER SET ISO8859_1 COLLATE FR_FR)
 RETURNS (NOM3 VARCHAR(20) CHARACTER SET ISO8859_1 COLLATE ISO8859_1)
 AS
 DECLARE VARIABLE NOM2 VARCHAR(20) CHARACTER SET ISO8859_1 COLLATE FR_CA;
BEGIN
 NOM2=NOM1;
 NOM3=NOM2;
 SUSPEND;
END !!
SET TERM ;!!
COMMIT;



"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SHOW PROCEDURE NEW_PROCEDURE;
SELECT * FROM NEW_PROCEDURE('TEST');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Procedure text:
=============================================================================
 DECLARE VARIABLE NOM2 VARCHAR(20) CHARACTER SET ISO8859_1 COLLATE FR_CA;
BEGIN
 NOM2=NOM1;
 NOM3=NOM2;
 SUSPEND;
END
=============================================================================
Parameters:
NOM1                              INPUT VARCHAR(20) CHARACTER SET ISO8859_1 COLLATE FR_FR
NOM3                              OUTPUT VARCHAR(20) CHARACTER SET ISO8859_1

NOM3
====================
TEST

"""

@pytest.mark.version('>=2.1')
def test_15_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

