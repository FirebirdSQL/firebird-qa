#coding:utf-8
#
# id:           bugs.core_1267
# title:        Small bug with default value for domains in PSQL
# decription:   
# tracker_id:   CORE-1267
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1267

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN BIT AS SMALLINT CHECK (VALUE IN (0,1) OR VALUE IS NULL);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^;

EXECUTE BLOCK
RETURNS (
  ID BIT)
AS
BEGIN
  SUSPEND;
END ^

set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
     ID
=======
 <null>

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

