#coding:utf-8
#
# id:           bugs.core_3599
# title:        Possible drop role RDB$ADMIN
# decription:   
# tracker_id:   CORE-3599
# min_versions: ['2.5.2']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    DROP ROLE RDB$ADMIN;
    COMMIT;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -DROP ROLE RDB$ADMIN failed
    -Cannot delete system SQL role RDB$ADMIN
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

