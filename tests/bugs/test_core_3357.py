#coding:utf-8
#
# id:           bugs.core_3357
# title:        Generators are set to 0 after restore
# decription:   
#                   NOTE: FB 4.x has incompatible behaviour with all previous versions since build 4.0.0.2131 (06-aug-2020):
#                   statement 'alter sequence <seq_name> restart with 0' changes rdb$generators.rdb$initial_value to -1 thus
#                   next call of gen_id(<seq_name>,1) will return 0 (ZERO!) rather than 1. 
#                   See also CORE-6084 and its fix: https://github.com/FirebirdSQL/firebird/commit/23dc0c6297825b2e9006f4d5a2c488702091033d
#                   This is considered as *expected* and is noted in doc/README.incompatibilities.3to4.txt
#               
#                   Because of this it was decided to create separate section for check FB 4.x results.
#                   Checked on 4.0.0.2164
#                
# tracker_id:   CORE-3357
# min_versions: ['2.5.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate sequence g1 start with 9223372036854775807 increment by -2147483647;
    recreate sequence g2 start with -9223372036854775808 increment by 2147483647;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  db_conn.close()
#  fbk = os.path.join(context['temp_directory'],'tmp.core_3942.fbk')
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,dsn,fbk])
#  runProgram('gbak',['-rep','-user',user_name,'-password',user_password,fbk,dsn])
#  sql='''show sequ g1;
#  show sequ g2;
#  '''
#  runProgram('isql',[dsn,'-user',user_name,'-pas',user_password],sql)
#  
#  if os.path.isfile(fbk):
#      os.remove(fbk)
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Generator G1, current value: 9223372036854775807, initial value: 9223372036854775807, increment: -2147483647
    Generator G2, current value: -9223372036854775808, initial value: -9223372036854775808, increment: 2147483647
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_3357_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """
    recreate sequence g1 start with 9223372036854775807 increment by -2147483647;
    recreate sequence g2 start with -9223372036854775808 increment by 2147483647;
    commit;
  """

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
# import os
#  db_conn.close()
#  fbk = os.path.join(context['temp_directory'],'tmp.core_3942.fbk')
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,dsn,fbk])
#  runProgram('gbak',['-rep','-user',user_name,'-password',user_password,fbk,dsn])
#  sql='''show sequ g1;
#  show sequ g2;
#  '''
#  runProgram('isql',[dsn,'-user',user_name,'-pas',user_password],sql)
#  
#  if os.path.isfile(fbk):
#      os.remove(fbk)
#---
#act_2 = python_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    Generator G1, current value: -9223372034707292162, initial value: 9223372036854775807, increment: -2147483647
    Generator G2, current value: 9223372034707292161, initial value: -9223372036854775808, increment: 2147483647
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_core_3357_2(db_2):
    pytest.fail("Test not IMPLEMENTED")


