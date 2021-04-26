#coding:utf-8
#
# id:           bugs.core_2227
# title:        Problem with column names with Accents and triggers
# decription:   
#               	28.02.2021
#               	Changed connection charset to UTF8 otherwise on Linux this test leads to 'ERROR' with issuing:
#               	====
#                       ISQL_STDERR
#                       Expected end of statement, encountered EOF
#                   ====
#                   Checked again on:
#                   1) Windows: 4.0.0.2372; 3.0.8.33416
#                   2) Linux:   4.0.0.2377
#                
# tracker_id:   CORE-2227
# min_versions: []
# versions:     2.1.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.2
# resources: None

substitutions_1 = []

init_script_1 = """
   RECREATE TABLE TESTING (
      "CÓDIGO" INTEGER
  );
 """

db_1 = db_factory(charset='ISO8859_1', sql_dialect=3, init=init_script_1)

test_script_1 = """
    SET TERM ^;
    CREATE TRIGGER TESTING_I FOR TESTING
    ACTIVE BEFORE INSERT POSITION 0
    AS
    BEGIN
      NEW."CÓDIGO" = 1;
    END ^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1.2')
def test_core_2227_1(act_1: Action):
    act_1.execute()

