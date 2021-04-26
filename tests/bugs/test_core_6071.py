#coding:utf-8
#
# id:           bugs.core_6071
# title:        Restore of encrypted backup of database with SQL dialect 1 fails
# decription:   
#               
#                   We create new database ('tmp_core_6071.fdb') and try to encrypt it using IBSurgeon Demo Encryption package
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
#                   After this we:
#                   1. Change temp DB state to full shutdown and bring it online - in order to be sure that we will able to drop this file later;
#                   2. Make backup of this temp DB, using gbak utility and '-KEYHOLDER <name_of_key_holder>' command switch.
#                      NB! According to additional explanation by Alex, ticket issue occured *only* when "gbak -KEYHOLDER ..." used rather than fbsvcmgr.
#                   3. Make restore from just created backup.
#                   4. Make validation of just restored database by issuing command "gfix -v -full ..."
#                      ( i.e. validate both data and metadata rather than online val which can check user data only).
#                   5. Check that NO errors occured on any above mentioned steps. Also check that backup and restore STDOUT logs contain expected 
#                      text about successful completition
#               
#                   Confirmed bug on 4.0.0.1485 (build date: 11-apr-2019), got error on restore:
#                       SQL error code = -817
#                       Metadata update statement is not allowed by the current database SQL dialect 1
#               
#                   Works fine on 4.0.0.1524, time ~8s.
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
# tracker_id:   CORE-6071
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('\\d+ BYTES WRITTEN', '')]

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
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#  
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_6071.fdb'
#  tmpbkp='$(DATABASE_LOCATION)'+'tmp_core_6071.fbk'
#  
#  gbak_backup_finish_ptn=re.compile('gbak:closing\\s+file,\\s+committing,\\s+and\\s+finishing.*', re.IGNORECASE)
#  gbak_restore_finish_ptn=re.compile('gbak:adjusting\\s+the\\s+ONLINE\\s+and\\s+FORCED\\s+WRITES\\s+.*', re.IGNORECASE)
#  
#  if os.path.isfile( tmpfdb ):
#      os.remove( tmpfdb )
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb, sql_dialect = 1 )
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
#  #---------- aux func for cleanup: ---------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  
#  
#  #-------------------------- shutdown temp DB and bring it online --------------------
#  
#  f_dbshut_log = open( os.path.join(context['temp_directory'],'tmp_dbshut_6071.log'), 'w')
#  subprocess.call( [ "gfix", 'localhost:'+tmpfdb, "-shut", "full", "-force", "0" ],
#                   stdout = f_dbshut_log,
#                   stderr = subprocess.STDOUT
#                 )
#  subprocess.call( [ "gfix", 'localhost:'+tmpfdb, "-online" ],
#                   stdout = f_dbshut_log,
#                   stderr = subprocess.STDOUT
#                 )
#  f_dbshut_log.close()
#  
#  #--------------------------- backup and restore --------------------------------------
#  fn_bkp_log=open( os.path.join(context['temp_directory'],'tmp_backup_6071.log'), 'w')
#  fn_bkp_err=open( os.path.join(context['temp_directory'],'tmp_backup_6071.err'), 'w')
#  
#  
#  subprocess.call([ "gbak.exe"
#                   ,"-b"
#                   ,"-v"
#                   ,"-KEYHOLDER", "KeyHolder"
#                   ,"-crypt", "DbCrypt"
#                   ,'localhost:' + tmpfdb
#                   ,tmpbkp
#                  ],
#                  stdout=fn_bkp_log, stderr=fn_bkp_err)
#  
#  fn_bkp_log.close()
#  fn_bkp_err.close()
#  
#  
#  fn_res_log=open( os.path.join(context['temp_directory'],'tmp_restore_6071.log'), 'w')
#  fn_res_err=open( os.path.join(context['temp_directory'],'tmp_restore_6071.err'), 'w')
#  
#  # C:\\FB SS\\gbak.exe -rep -KEYHOLDER KeyHolder C:\\FBTESTING\\qa\\misc\\C6071.fbk /:C:\\FBTESTING\\qa\\misc\\c6071.restored.FDB
#  subprocess.call([ "gbak"
#                   ,"-rep"
#                   ,"-v"
#                   ,"-KEYHOLDER", "KeyHolder"
#                   ,tmpbkp
#                   ,'localhost:' + tmpfdb
#                  ],
#                  stdout=fn_res_log, stderr=fn_res_err)
#  
#  fn_res_log.close()
#  fn_res_err.close()
#  
#  #-------------------------- validate just restored database --------------------
#  
#  f_valid_log = open( os.path.join(context['temp_directory'],'tmp_valid_6071.log'), 'w')
#  subprocess.call( [ "gfix", 'localhost:'+tmpfdb, "-v", "-full" ],
#                   stdout = f_valid_log,
#                   stderr = subprocess.STDOUT
#                 )
#  f_valid_log.close()
#  
#  #-----------------------------------------------
#  
#  # Check that all was fine:
#  
#  with open(f_dbshut_log.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED SHUTDOWN OUTPUT: ' + line)
#  
#  with open(fn_bkp_err.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED BACKUP STDERR: ' + line)
#  
#  with open(fn_res_err.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED RESTORE STDERR: ' + line)
#  
#  with open(f_dbshut_log.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED VALIDATION OUTPUT: ' + line)
#  
#  # gbak -b should finish with line:
#  #    gbak:closing file, committing, and finishing. 512 bytes written
#  with open(fn_bkp_log.name,'r') as f:
#      for line in f:
#          if gbak_backup_finish_ptn.search(line):
#              print('EXPECTED BACKUP FINISH FOUND: '+line.upper() )
#  
#  #gbak_backup_finish_ptn=re.compile('gbak:closing\\s+file,\\s+committing,\\s+and\\s+finishing.*', re.IGNORECASE)
#  
#  # gbak -c should finish with lines:
#  #    gbak:finishing, closing, and going home
#  #    gbak:adjusting the ONLINE and FORCED WRITES flags
#  #gbak_restore_finish_ptn=re.compile('gbak:adjusting\\s+the\\s+ONLINE\\s+and\\s+FORCED\\s+WRITES\\s+.*', re.IGNORECASE)
#  with open(fn_res_log.name,'r') as f:
#      for line in f:
#          if gbak_restore_finish_ptn.search(line):
#              print('EXPECTED RESTORE FINISH FOUND: '+line.upper() )
#  
#  
#  # Allow all file buffers to be flushed on disk before we will drop them:
#  time.sleep(1)
#  
#  # cleanup
#  ##########
#  
#  f_list = [ i.name for i in ( f_dbshut_log, fn_bkp_log, fn_bkp_err, fn_res_log, fn_res_err, f_valid_log ) ]
#  f_list += [ tmpfdb, tmpbkp ]
#  cleanup( f_list )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EXPECTED BACKUP FINISH FOUND: GBAK:CLOSING FILE, COMMITTING, AND FINISHING.
    EXPECTED RESTORE FINISH FOUND: GBAK:ADJUSTING THE ONLINE AND FORCED WRITES FLAGS
  """

@pytest.mark.version('>=4.0')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_6071_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


