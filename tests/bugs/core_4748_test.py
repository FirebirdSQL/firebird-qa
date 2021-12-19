#coding:utf-8
#
# id:           bugs.core_4748
# title:        Can not restore in FB 3.0 SuperServer from .fbk which source .fdb was created on 2.5.4 and moved to READ-ONLY before backed up
# decription:
# tracker_id:   CORE-4748
# min_versions: ['3.0']
# versions:     3.0
# qmid:

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core_4748_read_only_25.fbk', init=init_script_1, async_write=False)

test_script_1 = """
    set list on;
    select mon$read_only as restored_ro from mon$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESTORED_RO                     1
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

