#coding:utf-8
#
# id:           bugs.core_5039
# title:        Connecting to service with invalid servicename yields incorrect error message
# decription:   
#                   28.01.2019. 
#                   Name of service manager is ignored in FB 4.0, see http://tracker.firebirdsql.org/browse/CORE-5883
#                   ("service_mgr" to be cleaned out from connection string completely...")
#                   Disabled this test to be run on FB 4.0: added record to '%FBT_REPO%	ests\\qa4x-exclude-list.txt'.
#                   Added EMPTY section for FB version 4.0 in this .fbt as one more way to protect from running.
#                 
# tracker_id:   CORE-5039
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  db_conn.close()
#  runProgram('fbsvcmgr',['localhost:qwe_mnb_zxc_9','user','SYSDBA','password','masterkey','info_server_version'])
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Cannot attach to services manager
    -service qwe_mnb_zxc_9 is not defined
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_5039_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
     -- This section was intentionally left empty.
     -- No message should be in expected_* sections.
     -- It is STRONGLY RECOMMENDED to add this ticket
     -- in the 'excluded-list file:
     -- %FBT_REPO%	ests\\qa4x-exclude-list.txt
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)


@pytest.mark.version('>=4.0')
def test_core_5039_2(act_2: Action):
    act_2.execute()

