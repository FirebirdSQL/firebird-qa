#coding:utf-8
#
# id:           bugs.core_5077
# title:        ISQL does not show encryption status of database
# decription:   
#                   We create new database ('tmp_core_5077.fdb') and try to encrypt it usng IBSurgeon Demo Encryption package
#                   ( https://ib-aid.com/download-demo-firebird-encryption-plugin/ ; https://ib-aid.com/download/crypt/CryptTest.zip )
#                   License file plugins\\dbcrypt.conf with unlimited expiration was provided by IBSurgeon to Firebird Foundation (FF).
#                   This file was preliminary stored in FF Test machine.
#                   Test assumes that this file and all neccessary libraries already were stored into FB_HOME and %FB_HOME%\\plugins.
#               
#                   Anyone who wants to run this test on his own machine must
#                   1) download https://ib-aid.com/download/crypt/CryptTest.zip AND 
#                   2) PURCHASE LICENSE and get from IBSurgeon file plugins\\dbcrypt.conf with apropriate expiration date and other info.
#                   
#                   ################################################ ! ! !    N O T E    ! ! ! ##############################################
#                   FF tests storage (aka "fbt-repo") does not (and will not) contain any license file for IBSurgeon Demo Encryption package!
#                   #########################################################################################################################
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
#                   === NOTE-1 ===
#                   In case of "Crypt plugin DBCRYPT failed to load/607/335544351" check that all 
#                   needed files from IBSurgeon Demo Encryption package exist in %FB_HOME% and %FB_HOME%\\plugins
#                   %FB_HOME%:
#                       283136 fbcrypt.dll
#                      2905600 libcrypto-1_1-x64.dll
#                       481792 libssl-1_1-x64.dll
#               
#                   %FB_HOME%\\plugins:
#                       297984 dbcrypt.dll
#                       306176 keyholder.dll
#                          108 DbCrypt.conf
#                          856 keyholder.conf
#                   
#                   === NOTE-2 ===
#                   Version of DbCrypt.dll of october-2018 must be replaced because it has hard-coded 
#                   date of expiration rather than reading it from DbCrypt.conf !!
#               
#                   === NOTE-3 ===
#                   firebird.conf must contain following line:
#                       KeyHolderPlugin = KeyHolder
#               
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
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  
#  #--------------------------------------------
#  
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  fb_home = services.connect(host='localhost', user= user_name, password= user_password).get_home_directory()
#  
#  db_conn.close()
#  
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_5077.fdb'
#  
#  if os.path.isfile( tmpfdb ):
#      os.remove( tmpfdb )
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb )
#  con.close()
#  con=fdb.connect( dsn = 'localhost:'+tmpfdb )
#  cur = con.cursor()
#  cur.execute('alter database encrypt with dbcrypt key Red')
#  con.commit()
#  time.sleep(2)
#  #          ^
#  #          +-------- !! ALLOW BACKGROUND ENCRYPTION PROCESS TO COMPLETE ITS JOB !!
#  
#  con.close()
#  
#  #--------------------------------- run ISQL --------------------
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_5077.sql'), 'w')
#  f_isql_cmd.write('show database;')
#  f_isql_cmd.close()
#  
#  f_isql_log=open( os.path.join(context['temp_directory'], 'tmp_5077.log'), 'w')
#  f_isql_err=open( os.path.join(context['temp_directory'], 'tmp_5077.err'), 'w')
#  subprocess.call( [fb_home+'isql', 'localhost:' + tmpfdb, '-q', '-n', '-i', f_isql_cmd.name ], stdout=f_isql_log, stderr = f_isql_err)
#  f_isql_log.close()
#  f_isql_err.close()
#  
#  #---------------------------- shutdown temp DB --------------------
#  
#  f_dbshut_log = open( os.path.join(context['temp_directory'],'tmp_dbshut_5077.log'), 'w')
#  subprocess.call( [ "gfix", 'localhost:'+tmpfdb, "-shut", "full", "-force", "0" ],
#                   stdout = f_dbshut_log,
#                   stderr = subprocess.STDOUT
#                 )
#  f_dbshut_log.close()
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
#  time.sleep(1)
#  
#  # CLEANUP
#  #########
#  
#  f_list = [ i.name for i in ( f_isql_log, f_isql_err, f_isql_cmd, f_dbshut_log ) ]
#  f_list += [ tmpfdb ]
#  cleanup( f_list )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DATABASE ENCRYPTED
  """

@pytest.mark.version('>=3.0')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_5077_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


