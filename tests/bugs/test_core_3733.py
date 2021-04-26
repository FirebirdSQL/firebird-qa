#coding:utf-8
#
# id:           bugs.core_3733
# title:        GBAK fails to fix system generators while restoring
# decription:   
# tracker_id:   CORE-3733
# min_versions: []
# versions:     2.5.2
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3733.fbk', init=init_script_1)

test_script_1 = """
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.2')
def test_core_3733_1(act_1: Action):
    act_1.execute()

