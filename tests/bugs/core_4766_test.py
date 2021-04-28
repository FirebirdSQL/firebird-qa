#coding:utf-8
#
# id:           bugs.core_4766
# title:        AV when trying to manage users list using EXECUTE STATEMENT on behalf of non-sysdba user which has RDB$ADMIN role
# decription:   
#                   05.01.2020. Refactored in order to make its code more flexible because 3.0 and 4.0 have significant differences in stdout/stderr.
#                   Common SQL code was stored in fbt-repo
#               iles\\core_4766.sql with embedding variable names there from here:
#                       %(current_auth_plugin)s, %(dsn)s et al.
#               
#                   Content of this file is stored in variable 'sql_text' and this variable is changed using common Python rule for substitutions:
#                       sql_text % dict(globals(), **locals()
#               
#                   Then we save this variable to temporarily .sql script and run it.
#                   This action is done for two possible values of auth plugin (see var. current_auth_plugin): Srp and Legacy_UserManager.
#               
#                   As result, we have to compare only expected* data for different FB major versions.
#               
#                   ::: NB :::
#                   Only Legacy_UserManager is checked for FB 4.0. Srp has totally different behaviour, at  least for 4.0.0.1714.
#                   Sent letter to dimitr and alex, 05.01.2020 22:00.
#               
#                   Crash is reproduced on WI-T3.0.0.31374 Firebird 3.0 Beta 1 (build 24-nov-2014).
#               
#                   Checked on:
#                       4.0.0.1743 SS: 1.452s.
#                       4.0.0.1740 SC: 1.870s.
#                       4.0.0.1714 CS: 10.240s.
#                       3.0.6.33236 SS: 1.220s.
#                       3.0.5.33221 SC: 5.416s.
#                       3.0.5.33084 CS: 2.891s.
#               
#                
# tracker_id:   CORE-4766
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('TCPv.*', 'TCP'), ('.*After line \\d+.*', ''), ('find/delete', 'delete'), ('TABLE PLG\\$.*', 'TABLE PLG')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import subprocess
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  this_db = db_conn.database_name
#  db_conn.close()
#  
#  #--------------------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  #--------------------------------------------
#  
#  f_sql=open(os.path.join(context['files_location'],'core_4766.sql'),'r')
#  sql_text = f_sql.read()
#  f_sql.close()
#  
#  for current_auth_plugin in ('Srp', 'Legacy_UserManager'):
#      f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_core_4766.' + current_auth_plugin[:3] + '.sql'), 'w')
#      f_sql_chk.write( sql_text % dict(globals(), **locals()) )
#      flush_and_close( f_sql_chk )
#  
#      f_sql_log = open( '.'.join( (os.path.splitext( f_sql_chk.name )[0], 'log') ), 'w')
#      subprocess.call( [ context['isql_path'], '-q', '-i', f_sql_chk.name ], stdout = f_sql_log, stderr = subprocess.STDOUT)
#      flush_and_close( f_sql_log )
#  
#      with open( f_sql_log.name,'r') as f:
#          for line in f:
#              if line.strip():
#                  print( current_auth_plugin[:3] + ': ' + line )
#  
#      cleanup( (f_sql_log.name, f_sql_chk.name) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Srp: BOSS_SEC_NAME                   TMP_4766_BOSS
    Srp: BOSS_SEC_PLUGIN                 Srp
    Srp: BOSS_SEC_IS_ADMIN               <true>
    Srp: Statement failed, SQLSTATE = 28000
    Srp: add record error
    Srp: -no permission for INSERT access to TABLE PLG$SRP_VIEW

    Srp: MNGR_SEC_NAME                   <null>
    Srp: MNGR_SEC_PLUGIN                 <null>
    Srp: MNGR_SEC_IS_ADMIN               <null>
    Srp: Statement failed, SQLSTATE = 28000
    Srp: delete record error
    Srp: -no permission for DELETE access to TABLE PLG$SRP_VIEW


    Leg: BOSS_SEC_NAME                   TMP_4766_BOSS
    Leg: BOSS_SEC_PLUGIN                 Legacy_UserManager
    Leg: BOSS_SEC_IS_ADMIN               <true>
    Leg: Statement failed, SQLSTATE = 28000
    Leg: add record error
    Leg: -no permission for INSERT access to TABLE PLG$VIEW_USERS

    Leg: MNGR_SEC_NAME                   <null>
    Leg: MNGR_SEC_PLUGIN                 <null>
    Leg: MNGR_SEC_IS_ADMIN               <null>

    Leg: Statement failed, SQLSTATE = 28000
    Leg: find/delete record error
    Leg: -no permission for DELETE access to TABLE PLG$VIEW_USERS

  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


# version: 4.0
# resources: None

substitutions_2 = [('TCPv.*', 'TCP'), ('.*After line \\d+.*', ''), ('find/delete', 'delete'), ('TABLE PLG\\$.*', 'TABLE PLG')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
# 
#  import os
#  import sys
#  import subprocess
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  this_db = db_conn.database_name
#  db_conn.close()
#  
#  #--------------------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  
#  #--------------------------------------------
#  
#  f_sql=open(os.path.join(context['files_location'],'core_4766.sql'),'r')
#  sql_text = f_sql.read()
#  f_sql.close()
#  
#  # ::: NB :::
#  # Only Legacy_UserManager is checked for FB 4.0. Srp has totally different behaviour, at  least for 4.0.0.1714.
#  # Sent letter to dimitr and alex, 05.01.2020 22:00.
#  
#  for current_auth_plugin in ('Legacy_UserManager',):
#      f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_core_4766.' + current_auth_plugin[:3] + '.sql'), 'w')
#      f_sql_chk.write( sql_text % dict(globals(), **locals()) )
#      flush_and_close( f_sql_chk )
#  
#      f_sql_log = open( '.'.join( (os.path.splitext( f_sql_chk.name )[0], 'log') ), 'w')
#      subprocess.call( [ context['isql_path'], '-q', '-i', f_sql_chk.name ], stdout = f_sql_log, stderr = subprocess.STDOUT)
#      flush_and_close( f_sql_log )
#  
#      with open( f_sql_log.name,'r') as f:
#          for line in f:
#              if line.strip():
#                  print( current_auth_plugin[:3] + ': ' + line )
#  
#      cleanup( (f_sql_log.name, f_sql_chk.name) )
#  
#  '''
#   'substitutions':[
#      ('TCPv.*', 'TCP'),
#      ('.*After line \\d+.*', ''),
#      ('find/delete', 'delete'),
#      ('TABLE PLG\\$.*', 'TABLE PLG')
#    ]
#  '''
#  
#    
#---
#act_2 = python_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    Leg: BOSS_SEC_NAME                   TMP_4766_BOSS
    Leg: BOSS_SEC_PLUGIN                 Legacy_UserManager
    Leg: BOSS_SEC_IS_ADMIN               <true>

    Leg: Statement failed, SQLSTATE = 28000
    Leg: add record error
    Leg: -no permission for INSERT access to TABLE PLG$VIEW_USERS
    Leg: -Effective user is TMP_4766_BOSS

    Leg: MNGR_SEC_NAME                   <null>
    Leg: MNGR_SEC_PLUGIN                 <null>
    Leg: MNGR_SEC_IS_ADMIN               <null>

    Leg: Statement failed, SQLSTATE = 28000
    Leg: find/delete record error
    Leg: -no permission for DELETE access to TABLE PLG$VIEW_USERS
    Leg: -Effective user is TMP_4766_BOSS
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_2(db_2):
    pytest.fail("Test not IMPLEMENTED")


