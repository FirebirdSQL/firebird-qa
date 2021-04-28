#coding:utf-8
#
# id:           bugs.core_5939
# title:        Crash for "gbak -se -b database nul"
# decription:   
#                   Bug can be reproduced on WI-V2.5.9.27117 Classic (snapshot date: 29-sep-2018).
#                   All fine on WI-V2.5.9.27129.
#                   Also checked on:
#                       40sS, build 4.0.0.1479:
#                       40sC, build 4.0.0.1421:
#                       40Cs, build 4.0.0.1457:
#                       30sS, build 3.0.5.33115
#                       30sC, build 3.0.2.32658
#                       30Cs, build 3.0.4.33054
#                 
# tracker_id:   CORE-5939
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
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
#  
#  tmpfbk = 'tmp_core_5939.fbk'
#  tmpfbk='$(DATABASE_LOCATION)'+tmpfbk
#  
#  runProgram('gbak',['-b', dsn, tmpfbk, '-se'])
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    gbak: ERROR:service name parameter missing
    gbak:Exiting before completion due to errors
  """

@pytest.mark.version('>=2.5.9')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


