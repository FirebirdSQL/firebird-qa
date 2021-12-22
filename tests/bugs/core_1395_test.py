#coding:utf-8
#
# id:           bugs.core_1395
# title:        Few problems with domains's check constraints
# decription:   
# tracker_id:   CORE-1395
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1395-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST ( ID INTEGER );
CREATE DOMAIN TEST_DOMAIN AS INTEGER CHECK (EXISTS(SELECT * FROM TEST WHERE ID=VALUE));
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DROP TABLE TEST;
COMMIT;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-COLUMN TEST.ID
-there are 1 dependencies
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

