#coding:utf-8
#
# id:           bugs.core_5309
# title:        Backup created under FB2.5 can be restored in FB3.0.0.32419 but not under current snapshot (FB3.0.1.32556)
# decription:   
#                   Test does trivial attempt to restore database which was given by ticket starter as attached file.
#                   No further actions required. STDOUR and STDERR must be empty.
#               
#                   Confirmed on 4.0.0.258, got:
#                       GBAK_STDERR:
#                       gbak: ERROR:arithmetic exception, numeric overflow, or string truncation
#                       gbak: ERROR:    string right truncation
#                       gbak: ERROR:    expected length 67, actual 201
#                       gbak: ERROR:gds_$send failed
#                       gbak:Exiting before completion due to errors
#               
#                  All works fine on 3.0.1.32568 and 4.0.0.313.
#                
# tracker_id:   CORE-5309
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core5309.fbk', init=init_script_1)

test_script_1 = """
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.1')
def test_1(act_1: Action):
    act_1.execute()

