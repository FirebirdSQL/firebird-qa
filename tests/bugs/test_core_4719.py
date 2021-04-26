#coding:utf-8
#
# id:           bugs.core_4719
# title:        Message "Statement failed, SQLSTATE = 00000 + unknown ISC error 0" appears when issuing REVOKE ALL ON ALL FROM <existing_user>
# decription:   
# tracker_id:   CORE-4719
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('Statement failed, SQLSTATE.*', ''), ('record not found for user:.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    drop user tmp$c4719;
    commit;
    create user tmp$c4719 password '123';
    commit;
    revoke all on all from tmp$c4719;
    commit;
    drop user tmp$c4719;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Warning: ALL on ALL is not granted to TMP$C4719.
  """

@pytest.mark.version('>=2.5')
def test_core_4719_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

