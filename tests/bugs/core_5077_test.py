#coding:utf-8
#
# id:           bugs.core_5077
# title:        ISQL 'SHOW DATABASE' command does not show encryption status of database
# decription:   
#                   We create new database ('tmp_core_5077.fdb') and try to encrypt it usng IBSurgeon Demo Encryption package
#                   ( https://ib-aid.com/download-demo-firebird-encryption-plugin/ ; https://ib-aid.com/download/crypt/CryptTest.zip )
#                   License file plugins\\dbcrypt.conf with unlimited expiration was provided by IBSurgeon to Firebird Foundation (FF).
#                   This file was preliminary stored in FF Test machine.
#                   Test assumes that this file and all neccessary libraries already were stored into FB_HOME and %FB_HOME%\\plugins.
#               
#                   After test database will be created, we try to encrypt it using 'alter database encrypt with <plugin_name> ...' command
#                   (where <plugin_name> = dbcrypt - name of .dll in FB_HOME\\plugins\\ folder that implements encryption).
#                   Then we allow engine to complete this job - take delay about 1..2 seconds BEFORE detach from database.
#               
#                   After this we run ISQL with 'SHOW DATABASE' command. Its output has to contain string 'Database encrypted'.
#               
#                   Finally, we change this temp DB state to full shutdown in order to have 100% ability to drop this file.
#               
#                   Checked on: 4.0.0.1629: OK, 6.264s; 3.0.5.33179: OK, 4.586s.
#               
#                   13.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 4.0.0.2416
#                     Linux:   4.0.0.2416
#                   Note: different names for encryption plugin and keyholde rare used for Windows vs Linux:
#                      PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else '"fbSampleDbCrypt"'
#                      KHOLDER_NAME = 'KeyHolder' if os.name == 'nt' else "fbSampleKeyHolder"
#                
# tracker_id:   CORE-5077
# min_versions: ['3.0.0']
# versions:     3.0
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
#  import os
#  import time
#  import subprocess
#  import re
#  import fdb
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  engine = db_conn.engine_version
#  db_conn.close()
#  
#  #--------------------------------------------
#  
#  def flush_and_close( file_handle ):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#  
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb') and file_handle.name != os.devnull:
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if type(f_names_list[i]) == file:
#            del_name = f_names_list[i].name
#         elif type(f_names_list[i]) == str:
#            del_name = f_names_list[i]
#         else:
#            print('Unrecognized type of element:', f_names_list[i], ' - can not be treated as file.')
#            print('type(f_names_list[i])=',type(f_names_list[i]))
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_5077.fdb'
#  
#  cleanup( (tmpfdb,) )
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb )
#  
#  # 14.04.2021.
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else ( '"fbSampleDbCrypt"' if engine >= 4.0 else '"DbCrypt_example"')
#  KHOLDER_NAME = 'KeyHolder' if os.name == 'nt' else "fbSampleKeyHolder"
#  
#  cur = con.cursor()
#  cur.execute('alter database encrypt with %(PLUGIN_NAME)s key Red' % locals())
#  ### DOES NOT WORK ON LINUX! ISSUES 'TOKEN UNKNOWN' !! >>> con.execute_immediate('alter database encrypt with %(PLUGIN_NAME)s key Red' % locals()) // sent letter to Alex and dimitr, 14.04.2021
#  con.commit()
#  time.sleep(2)
#  #          ^
#  #          +-------- !! ALLOW BACKGROUND ENCRYPTION PROCESS TO COMPLETE ITS JOB !!
#  
#  con.close()
#  
#  ########################################
#  # run ISQL with 'SHOW DATABASE' command:
#  ########################################
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_5077.sql'), 'w')
#  f_isql_cmd.write('show database;')
#  flush_and_close( f_isql_cmd )
#  
#  f_isql_log=open( os.path.join(context['temp_directory'], 'tmp_5077.log'), 'w')
#  f_isql_err=open( os.path.join(context['temp_directory'], 'tmp_5077.err'), 'w')
#  subprocess.call( [context['isql_path'], 'localhost:' + tmpfdb, '-q', '-n', '-i', f_isql_cmd.name ], stdout=f_isql_log, stderr = f_isql_err)
#  flush_and_close( f_isql_log )
#  flush_and_close( f_isql_err )
#  
#  #---------------------------- shutdown temp DB --------------------
#  
#  f_dbshut_log = open( os.path.join(context['temp_directory'],'tmp_dbshut_5077.log'), 'w')
#  subprocess.call( [ context['gfix_path'], 'localhost:'+tmpfdb, "-shut", "full", "-force", "0" ],
#                   stdout = f_dbshut_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_dbshut_log )
#  
#  allowed_patterns = (
#       re.compile( 'Database(\\s+not){0,1}\\s+encrypted\\.*', re.IGNORECASE),
#  )
#  
#  with open( f_isql_log.name,'r') as f:
#      for line in f:
#          match2some = filter( None, [ p.search(line) for p in allowed_patterns ] )
#          if match2some:
#              print( (' '.join( line.split()).upper() ) )
#  
#  with open( f_isql_err.name,'r') as f:
#      for line in f:
#          print("Unexpected error when doing 'SHOW DATABASE': "+line)
#  
#  with open( f_dbshut_log.name,'r') as f:
#      for line in f:
#          print("Unexpected error on SHUTDOWN temp database: "+line)
#  
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  
#  cleanup( ( f_isql_log, f_isql_err, f_isql_cmd, f_dbshut_log,tmpfdb )  )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DATABASE ENCRYPTED
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


