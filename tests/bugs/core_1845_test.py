#coding:utf-8
#
# id:           bugs.core_1845
# title:        Some standard calls show server installation directory to regular users
# decription:
#                  Instead of usage 'resource:test_user' (as it was before) we create every time this test run user TMP$C1845
#                  and make test connect to database with login = this user in order to check ability to make attach.
#                  Then we do subsequent run of FBSVCMGR utility with passing ONE of following options from 'Information requests'
#                  group:
#                    info_server_version
#                    info_implementation
#                    info_user_dbpath
#                    info_get_env
#                    info_get_env_lock
#                    info_get_env_msg
#                    info_svr_db_info
#                    info_version
#                  NOTE: option 'info_capabilities' was introduces only in 3.0. Its output differs on Classic vs SS and SC.
#                  Currently this option is NOT passed to fbsvcmgr.
#
# tracker_id:   CORE-1845
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         bugs.core_1845

import pytest
from firebird.qa import db_factory, python_act, Action, user_factory, User
from firebird.driver import DatabaseError

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#
#  # Refactored 05-JAN-2016: removed dependency on recource 'test_user' because this lead to:
#  # UNTESTED: bugs.core_1845
#  # Add new user
#  # Unexpected stderr stream received from GSEC.
#  # (i.e. test remained in state "Untested" because of internal error in gsec while creating user 'test' from resource).
#  # Checked on WI-V2.5.5.26952 (SC), WI-V3.0.0.32266 (SS/SC/CS).
#
#  import os
#  import subprocess
#  import time
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  sql_create_user='''    drop user tmp$c1845;
#      commit;
#      create user tmp$c1845 password 'QweRtyUi';
#      commit;
#      connect '%s' user 'TMP$C1845' password 'QweRtyUi';
#      set list on;
#      select current_user who_am_i from rdb$database;
#      quit;
#  ''' % dsn
#
#  sqllog=open( os.path.join(context['temp_directory'],'tmp_user_1845.log'), 'w')
#  sqllog.close()
#  runProgram('isql',[dsn,'-user',user_name,'-pas',user_password,'-q','-m', '-o', sqllog.name], sql_create_user)
#
#
#  fn_log=open( os.path.join(context['temp_directory'],'tmp_fbsvc_1845.log'), 'w')
#
#  svc_list=["info_server_version","info_implementation","info_user_dbpath","info_get_env","info_get_env_lock","info_get_env_msg","info_svr_db_info","info_version"]
#
#  for i in range(len(svc_list)):
#      fn_log.write("Check service '"+svc_list[i]+"':")
#      fn_log.write("\\n")
#      fn_log.seek(0,2)
#      subprocess.call([ context['fbsvcmgr_path'],"localhost:service_mgr","user","TMP$C1845","password","QweRtyUi", svc_list[i]]
#                        ,stdout=fn_log
#                        ,stderr=fn_log
#                     )
#      fn_log.write("\\n")
#
#  flush_and_close( fn_log )
#
#  # CLEANUP: drop user that was temp-ly created for this test:
#  ##########
#  runProgram('isql', [dsn, '-q','-m', '-o', sqllog.name], 'drop user tmp$c1845; commit;')
#
#  # Check content of files: 1st shuld contain name of temply created user, 2nd should be with error during get FB log:
#
#  with open( sqllog.name,'r') as f:
#      print(f.read())
#
#  # Print output of fbsvcmgr but: 1) remove exceessive whitespaces from lines; 2) transform text to uppercase
#  # (in order to reduce possibility of mismatches in case of minor changes that can occur in future versions of fbsvcmgr)
#
#  with open( fn_log.name,'r') as f:
#      for line in f:
#          print( ' '.join(line.split()).upper() )
#
#  # Do not remove this pause: on Windows closing of handles can take some (small) time.
#  # Otherwise Windows(32) access error can raise here.
#  time.sleep(1)
#
#  cleanup( (sqllog.name, fn_log.name) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

user_1 = user_factory('db_1', name='TMP$C1845', password='QweRtyUi')

@pytest.mark.version('>=2.5')
def test_1(act_1: Action, user_1: User):
    with act_1.connect_server(user=user_1.name, password=user_1.password) as srv:
        with pytest.raises(DatabaseError, match='.*requires SYSDBA permissions.*'):
            print(srv.info.security_database)
        with pytest.raises(DatabaseError, match='.*requires SYSDBA permissions.*'):
            print(srv.info.home_directory)
        with pytest.raises(DatabaseError, match='.*requires SYSDBA permissions.*'):
            print(srv.info.lock_directory)
        with pytest.raises(DatabaseError, match='.*requires SYSDBA permissions.*'):
            print(srv.info.message_directory)
        with pytest.raises(DatabaseError, match='.*requires SYSDBA permissions.*'):
            print(srv.info.attached_databases)

