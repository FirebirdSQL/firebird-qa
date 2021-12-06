#coding:utf-8
#
# id:           bugs.core_5270
# title:        FBSVCMGR does not produce error while attempting to shutdown a database without specified timeout (prp_force_shutdown N)
# decription:
#                  Confirmed bug on 4.0.0.258 (no error message is produced), all fine on 4.0.0.316 and 3.0.1.32570
#
# tracker_id:   CORE-5270
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#  db_file="$(DATABASE_LOCATION)bugs.core_5270.fdb"
#
#  runProgram('fbsvcmgr',['localhost:service_mgr', 'action_properties', 'dbname', db_file, 'prp_shutdown_mode', 'prp_sm_single'])
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stderr_1 = """
    must specify type of shutdown
"""

@pytest.mark.version('>=3.0.1')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.svcmgr(switches=['action_properties', 'dbname', str(act_1.db.db_path),
                           'prp_shutdown_mode', 'prp_sm_single'])
    assert act_1.clean_stderr == act_1.clean_expected_stderr


