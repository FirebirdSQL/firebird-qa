#coding:utf-8
#
# id:           bugs.core_4480
# title:        ISQL issues warning: "Bad debug info format" when connect to database with stored function after it`s restoring
# decription:   
# tracker_id:   CORE-4480
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    --    Note: core4480.fbk was created by WI-T3.0.0.30809 Firebird 3.0 Alpha 2.
    --    Retoring of this file in WI-T3.0.0.30809 finishes with:
    --    gbak: WARNING:function FN_A is not defined
    --    gbak: WARNING:    module name or entrypoint could not be found
    --    gbak: WARNING:function FN_A is not defined
    --    gbak: WARNING:    module name or entrypoint could not be found
    --    2) Attempt `execute procedure sp_a;` - leads to:
    --    Statement failed, SQLSTATE = 39000
    --    invalid request BLR at offset 29
    --    -function FN_A is not defined
    --    -module name or entrypoint could not be found
    --    -Error while parsing procedure SP_A's BLR
  """

db_1 = db_factory(from_backup='core4480.fbk', init=init_script_1)

test_script_1 = """
    execute procedure sp_a;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_4480_1(act_1: Action):
    act_1.execute()

