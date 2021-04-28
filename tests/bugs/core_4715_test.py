#coding:utf-8
#
# id:           bugs.core_4715
# title:        Restore of shadowed database fails using -k ("restore without shadow") switch
# decription:   
# tracker_id:   CORE-4715
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!HASH_IN_SOURCE|RDB\\$SHADOW_NUMBER|HASH_IN_RESTORED|Attributes).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_1 = """
    -- Confirmed on WI-T3.0.0.31374:
    -- command "gbak -rep -k c4715.fbk -user SYSDBA -pas masterke localhost/3000:<path>\\c4715-new.FDB"
    -- produces:
    -- gbak: ERROR:DELETE operation is not allowed for system table RDB$FILES
    -- gbak:Exiting before completion due to errors
    recreate table test(s varchar(30));
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  
#  shd=os.path.join(context['temp_directory'],'core_4715.shd')
#  script = '''create shadow 1 '%s'; commit; insert into test select 'line #'||lpad(row_number()over(), 3, '0') from rdb$types rows 200; commit; set list on; select hash(list(s)) hash_in_source from test; select * from rdb$files;''' % shd
#  runProgram('isql',[dsn,'-q','-user',user_name,'-password',user_password],script)
#  runProgram('gstat',[shd,'-h','-user',user_name,'-password',user_password])
#  fbk = os.path.join(context['temp_directory'],'core_4715-shadowed.fbk')
#  fbn = os.path.join(context['temp_directory'],'core_4715-restored.fdb')
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,dsn,fbk])
#  runProgram('gbak',['-rep','-k','-user',user_name,'-password',user_password,fbk,fbn])
#  script = '''set list on; select hash(list(s)) hash_in_restored from test;'''
#  runProgram('isql',[fbn,'-q','-user',user_name,'-password',user_password],script)
#  if os.path.isfile(fbk):
#      os.remove(fbk)
#  if os.path.isfile(fbn):
#      os.remove(fbn)
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
Creating shadow...
HASH_IN_SOURCE                  1499836372373901520
RDB$SHADOW_NUMBER               1
Attributes		force write, active shadow
HASH_IN_RESTORED                1499836372373901520
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


