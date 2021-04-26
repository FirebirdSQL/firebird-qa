#coding:utf-8
#
# id:           bugs.core_4648
# title:        no permission for CREATE access to DATABASE (for RDB$ADMIN)
# decription:   
# tracker_id:   CORE-4648
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set wng off;
    create or alter user tmp$c4648 password '123' revoke admin role;
    commit;
    revoke all on all from tmp$c4648;
    -- 'create ... grant admin role' or 'grant rdb$admin' are NOT neccessary 
    -- for enabling to creating database by non-sysdba user:
    grant create database to user tmp$c4648;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  
#  print ('Starting backup...')
#  fbk = os.path.join(context['temp_directory'],'tmp4648.fbk')
#  fdn = 'localhost:'+os.path.join(context['temp_directory'],'tmp4648.tmp')
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,dsn,fbk])
#  print ('Backup finished.')
#  print ('Starting restore using NON sysdba user account...')
#  runProgram('gbak',['-rep','-user','TMP$C4648','-password','123',fbk,fdn])
#  print ('Restore using NON sysdba user account finished.')
#  if os.path.isfile(fbk):
#      print ('Delete backup file...')
#      os.remove(fbk)
#      print ('Backup file deleted.')
#  
#  script = '''
#      set list on;
#      select 
#           a.mon$user as "Who am I:"
#          ,left(a.mon$remote_protocol,3) as "Used protocol:"
#          ,iif(m.mon$database_name containing 'tmp4648.tmp','YES','NO! ' || m.mon$database_name ) as "Connected to restored DB ?"
#          ,m.mon$owner as "Owner of DB is:"
#      from mon$attachments a, mon$database m 
#      where a.mon$attachment_id=current_connection;
#      commit;
#      drop database;
#  '''
#  print ('Starting ISQL using NON sysdba user account...')
#  runProgram('isql',[fdn,'-q','-user','tmp$c4648','-pas','123'],script)
#  print ('ISQL using NON sysdba user account finished.')
#  
#  script='''revoke create database from user tmp$c4648;
#  drop user tmp$c4648;
#  commit;
#  '''
#  runProgram('isql',[dsn,'-q','-user',user_name,'-password',user_password],script)
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Starting backup...
    Backup finished.
    Starting restore using NON sysdba user account...
    Restore using NON sysdba user account finished.
    Delete backup file...
    Backup file deleted.
    Starting ISQL using NON sysdba user account...
    Who am I:                       TMP$C4648
    Used protocol:                  TCP
    Connected to restored DB ?      YES
    Owner of DB is:                 TMP$C4648
    ISQL using NON sysdba user account finished.
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_4648_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


