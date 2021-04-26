#coding:utf-8
#
# id:           bugs.core_5140
# title:        Wrong error message when user tries to set number of page buffers into not supported value
# decription:   
#                
# tracker_id:   CORE-5140
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('range.*', 'range')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# runProgram('gfix',['-user',user_name,'-pas',user_password,'-b','1',dsn])
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    bad parameters on attach or create database
    -Attempt to set in database number of buffers which is out of acceptable range [50:131072]
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_5140_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


