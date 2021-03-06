#coding:utf-8
#
# id:           bugs.core_5887_trusted_role
# title:        Allow the use of management statements in PSQL blocks: check only TRUSTED ROLE
# decription:   
#                   Role can be set as TRUSTED when following conditions are true:
#                   * BOTH AuthServer and AuthClient parameters from firebird.conf contain 'Win_Sspi' as plugin, in any place;
#                   * current OS user has admin rights;
#                   * OS environment has *no* variables ISC_USER and ISC_PASSWORD (i.e. they must be UNSET);
#                   * Two mappings are created (both uses plugin win_sspi):
#                   ** from any user to user;
#                   ** from predefined_group domain_any_rid_admins to role <role_to_be_trusted>
#               
#                   Connect to database should be done in form: CONNECT '<computername>:<our_database>' role <role_to_be_trusted>',
#                   and after this we can user 'SET TRUSTED ROLE' statement.
#               
#                   This test checks that statement 'SET TRUSTED ROLE' can be used within PSQL block rather than as DSQL.
#               
#                   Checked on: 4.0.0.1457: OK, 2.602s.
#                   25.04.2020: added command to obtain %FB_HOME% folder in order to make call of ISQL as fully qualified executable.
#                   Checked on 4.0.0.1935 SS/CS (both on Windows 8.1 (IMAGE-PC1) and Windows-2008 R2 (IBSurgeon-2008) hosts).
#               
#                   Thanks to Alex for suggestions.
#                
# tracker_id:   CORE-5887
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import re
#  import time
#  import subprocess
#  from subprocess import Popen
#  from fdb import services
#  import socket
#  import getpass
#  
#  #---------------------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      os.fsync(file_handle.fileno())
#  
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#  
#  #--------------------------------------------
#  
#  # 23.08.2020: !!! REMOVING OS-VARIABLE ISC_USER IS MANDATORY HERE !!!
#  # This variable could be set by other .fbts which was performed before current within batch mode (i.e. when fbt_run is called from <rundaily>)
#  # NB: os.unsetenv('ISC_USER') actually does NOT affect on content of os.environ dictionary, see: https://docs.python.org/2/library/os.html
#  # We have to remove OS variable either by os.environ.pop() or using 'del os.environ[...]', but in any case this must be enclosed intro try/exc:
#  #os.environ.pop('ISC_USER')
#  try:
#      del os.environ["ISC_USER"]
#  except KeyError as e:
#      pass
#  
#  
#  THIS_DBA_USER=user_name
#  THIS_DBA_PSWD=user_password
#  
#  THIS_COMPUTER_NAME = socket.gethostname()
#  CURRENT_WIN_ADMIN = getpass.getuser()
#  
#  THIS_FDB = db_conn.database_name
#  db_conn.close()
#  
#  fb_home = services.connect(host='localhost', user= user_name, password= user_password).get_home_directory()
#  
#  f_sql_cmd = open( os.path.join(context['temp_directory'],'tmp_check_5887.sql'), 'w', buffering=0)
#  
#  f_sql_txt='''
#      set bail on;
#      -- set echo on;
#      connect 'localhost:%(THIS_FDB)s' user %(THIS_DBA_USER)s password '%(THIS_DBA_PSWD)s';
#      create role tmp$role_5887;
#      commit;
#      grant tmp$role_5887 to "%(THIS_COMPUTER_NAME)s\\%(CURRENT_WIN_ADMIN)s";
#      commit;
#  
#      -- We have to use here "create mapping trusted_auth ... from any user to user" otherwise get
#      -- Statement failed, SQLSTATE = 28000 /Missing security context for C:\\FBTESTING\\QA\\MISC\\C5887.FDB
#      -- on connect statement which specifies COMPUTERNAME:USERNAME instead path to DB:
#      create or alter mapping trusted_auth using plugin win_sspi from any user to user;
#  
#      -- We have to use here "create mapping win_admins ... DOMAIN_ANY_RID_ADMINS" otherwise get
#      -- Statement failed, SQLSTATE = 0P000 / Your attachment has no trusted role
#  
#      create or alter mapping win_admins using plugin win_sspi from predefined_group domain_any_rid_admins to role tmp$role_5887;
#      commit;
#  
#      connect '%(THIS_COMPUTER_NAME)s:%(THIS_FDB)s' role tmp$role_5887;
#  
#      --show mapping;
#  
#      set list on;
#      select 'point-1' as msg, a.mon$role,a.mon$auth_method from mon$attachments a where mon$attachment_id = current_connection;
#  
#      set term ^;
#      execute block as
#      begin
#          set trusted role;
#      end
#      ^
#      set term ;^
#      commit;
#  
#      connect '%(THIS_COMPUTER_NAME)s:%(THIS_FDB)s';
#      
#      select 'point-2' as msg, a.mon$role, a.mon$auth_method from mon$attachments a where mon$attachment_id = current_connection;
#      commit;
#  
#      connect 'localhost:%(THIS_FDB)s' user %(THIS_DBA_USER)s password '%(THIS_DBA_PSWD)s';
#      drop mapping trusted_auth;
#      drop mapping WIN_ADMINS;
#      commit;
#      --set bail off;
#      --show mapping;
#  ''' % locals()
#  
#  f_sql_cmd.write(f_sql_txt)
#  flush_and_close( f_sql_cmd )
#  
#  
#  f_sql_log=open( os.path.join(context['temp_directory'],'tmp_5887_trusted_role.log'), 'w', buffering=0)
#  subprocess.call( [ fb_home + "isql", "-q", "-i", f_sql_cmd.name ], stdout=f_sql_log, stderr=subprocess.STDOUT )
#  flush_and_close( f_sql_log )
#  
#  with open( f_sql_log.name,'r') as f:
#      for line in f:
#          print(line)
#  
#  cleanup( [x.name for x in  (f_sql_cmd, f_sql_log)] )
#  
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             point-1
    MON$ROLE                        TMP$ROLE_5887                                                                                                                                                                                                                                               
    MON$AUTH_METHOD                 Mapped from Win_Sspi

    MSG                             point-2
    MON$ROLE                        TMP$ROLE_5887                                                                                                                                                                                                                                               
    MON$AUTH_METHOD                 Mapped from Win_Sspi

  """

@pytest.mark.version('>=4.0')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


