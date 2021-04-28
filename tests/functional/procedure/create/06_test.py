#coding:utf-8
#
# id:           functional.procedure.create.06
# title:        CREATE PROCEDURE - PSQL Stataments - SUSPEND
# decription:   CREATE PROCEDURE - PSQL Stataments - SUSPEND
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.procedure.create.create_procedure_06

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
CREATE PROCEDURE test RETURNS(id INT)AS
BEGIN
  ID=4;
  SUSPEND;
  ID=5;
  SUSPEND;
END ^
SET TERM ;^
commit;
SHOW PROCEDURE test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Procedure text:
=============================================================================

BEGIN
  ID=4;
  SUSPEND;
  ID=5;
  SUSPEND;
END
=============================================================================
Parameters:
ID                                OUTPUT INTEGER
"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

