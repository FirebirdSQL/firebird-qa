#coding:utf-8
#
# id:           bugs.core_6412
# title:        Firebird is freezing when trying to manage users via triggers
# decription:   
#                   Confirmed hang on 4.0.0.2214
#               
#                   Checked on 4.0.0.2249 - no hang, but if this test runs in loop, w/o pauses for at least ~4s, then starting from 2nd run following fail raises:
#                      Statement failed, SQLSTATE = 08006
#                      Error occurred during login, please check server firebird.log for details
#                      Error occurred during login, please check server firebird.log for details
#                   This was because of: http://tracker.firebirdsql.org/browse/CORE-6441 (fixed).
#               
#                   Content of firebird.log will be added with following lines:
#                      Srp Server
#                      connection shutdown
#                      Database is shutdown.
#                   Sent report to Alex et al, 09.11.2020.
#                
# tracker_id:   CORE-6412
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('\t+', ' '), ('TCPv.*', 'TCP')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import time
#  import subprocess
#  import shutil
#  import uuid
#  from fdb import services
#  
#  svc = services.connect(host='localhost', user = user_name, password = user_password)
#  fb_home=svc.get_home_directory()
#  svc.close()
#  
#  dbconf = os.path.join(fb_home,'databases.conf')
#  dbcbak = os.path.join(fb_home,'databases.bak')
#  
#  try:
#      del os.environ["ISC_USER"]
#  except KeyError as e:
#      pass
#  
#  #--------------------------------------------
#  
#  def svc_get_fb_log( fb_home, f_fb_log ):
#  
#    global subprocess
#    subprocess.call( [ fb_home + "fbsvcmgr",
#                       "localhost:service_mgr",
#                       "action_get_fb_log"
#                     ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
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
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#  
#  #--------------------------------------------
#  
#  fdb_test = os.path.join(context['temp_directory'],'tmp_6412.fdb')
#  
#  
#  # NB: fb_home is full path to FB instance home (with trailing slash).
#  shutil.copy2( dbconf, dbcbak )
#  
#  tmp_alias = 'self_security_6412'
#  
#  alias_data='''
#  
#  # Added temporarily for executing test core_6412.fbt
#  %(tmp_alias)s = %(fdb_test)s {
#      # RemoteAccess = true
#      SecurityDatabase = %(tmp_alias)s
#  }
#  ''' % locals()
#  
#  f_dbconf=open(fb_home+'databases.conf','a')
#  f_dbconf.seek(0, 2)
#  f_dbconf.write( alias_data )
#  flush_and_close( f_dbconf )
#  
#  cleanup( (fdb_test,) )
#  
#  sql_init='''
#      set bail on;
#      create database '%(tmp_alias)s';
#      alter database set linger to 0;
#      create user SYSDBA password 'QweRty' using plugin Srp;
#      commit;
#  
#      connect 'localhost:%(tmp_alias)s' user sysdba password 'QweRty';
#  
#      set list on;
#      select a.mon$remote_protocol,
#             d.mon$sec_database
#      from mon$attachments a cross join mon$database d
#      where a.mon$attachment_id = current_connection;
#  
#      CREATE TABLE USERS
#      (
#        AUTHENTICATION VARCHAR(32) CHARACTER SET WIN1252 COLLATE WIN_PTBR
#      );
#      COMMIT;
#  
#      SET TERM ^ ;
#      CREATE TRIGGER USERS_AI_AU_AD FOR USERS
#      ACTIVE AFTER INSERT OR UPDATE OR DELETE POSITION 0
#      AS
#      BEGIN
#      	IF ((OLD.AUTHENTICATION IS NOT NULL) AND ((NEW.AUTHENTICATION IS NULL) OR (OLD.AUTHENTICATION<>NEW.AUTHENTICATION))) THEN
#      	BEGIN
#             EXECUTE STATEMENT 'REVOKE RDB$ADMIN FROM "' || OLD.AUTHENTICATION || '" GRANTED BY "SYSDBA"';
#             EXECUTE STATEMENT 'DROP USER "' || OLD.AUTHENTICATION || '" USING PLUGIN SRP';
#          END
#      	
#      	IF ((NEW.AUTHENTICATION IS NOT NULL) AND ((OLD.AUTHENTICATION IS NULL) OR (OLD.AUTHENTICATION<>NEW.AUTHENTICATION))) THEN
#      	BEGIN
#      		   EXECUTE STATEMENT 'GRANT RDB$ADMIN TO "' || NEW.AUTHENTICATION || '" GRANTED BY "SYSDBA"';
#      		   EXECUTE STATEMENT 'CREATE OR ALTER USER "' || NEW.AUTHENTICATION || '" SET PASSWORD ''123456'' USING PLUGIN SRP GRANT ADMIN ROLE';
#      	END
#      END^
#      SET TERM ; ^
#      COMMIT; 
#  
#      INSERT INTO USERS (AUTHENTICATION) VALUES ('AAA');
#      COMMIT; 
#  
#  
#      UPDATE USERS SET AUTHENTICATION='BBB' WHERE AUTHENTICATION='AAA';
#      COMMIT; 
#  
#      set list on;
#      select 'Completed' as result from rdb$database;
#      quit;
#  
#  ''' % locals()
#  
#  runProgram( 'isql',[ '-q' ], sql_init)
#  runProgram( 'gfix',[ '-shut', 'full', '-force', '0', 'localhost:' + fdb_test, '-user', 'SYSDBA', '-pas', 'QweRty' ])
#  
#  shutil.move( dbcbak, dbconf )
#  
#  cleanup( (fdb_test,) )
#  
#  # This delay is necessary for running this test multiple times (in loop) on SS and SC.
#  # Otherwise we get runtime error "SQLSTATE = 08006 / Error occurred during login, please check server firebird.log"
#  # and firebird.log will be filled with: "Srp Server / connection shutdown / Database is shutdown."
#  # Delay must be not less than 4 seconds. Tested on 4.0.0.2249.
#  #############
#  # 03-mar-2021: can be deleted (related to CORE-6441) >>> time.sleep(4)
#  #############
#  
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MON$REMOTE_PROTOCOL             TCPv6
    MON$SEC_DATABASE                Self
    RESULT                          Completed
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


