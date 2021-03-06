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
#                   16.04.2021.
#                   Changed code: database is created in dialect 3, then encrypted and after this we apply 'gfix -sql_dialect 1' to it.
#                   Unfortunately, I could not find the way how to make it work on Linux: attempt to backup (gbak -KEYHOLDER ... -crypt ... ) fails with:
#                       gbak: ERROR:unsuccessful metadata update
#                       gbak: ERROR:    ALTER DATABASE failed
#                       gbak: ERROR:    Error loading plugin FBSAMPLEDBCRYPT
#                       gbak: ERROR:    Module /var/tmp/fb40tmp/plugins/FBSAMPLEDBCRYPT does not contain plugin FBSAMPLEDBCRYPT type 9
#                   (after file libfbSampleDbCrypt.so was copied to libFBSAMPLEDBCRYPT.so)
#               
#                   Test remains WINDOWS only.
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
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_6071.fdb'
#  tmpbkp='$(DATABASE_LOCATION)'+'tmp_core_6071.fbk'
#  
#  gbak_backup_finish_ptn=re.compile('gbak:closing\\s+file,\\s+committing,\\s+and\\s+finishing.*', re.IGNORECASE)
#  gbak_restore_finish_ptn=re.compile('gbak:adjusting\\s+the\\s+ONLINE\\s+and\\s+FORCED\\s+WRITES\\s+.*', re.IGNORECASE)
#  
#  cleanup( (tmpfdb,) )
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb)
#  cur = con.cursor()
#  
#  # 14.04.2021.
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else '"fbSampleDbCrypt"'
#  KHOLDER_NAME = 'KeyHolder' if os.name == 'nt' else "fbSampleKeyHolder"
#  
#  ##############################################
#  # WARNING! Do NOT use 'connection_obj.execute_immediate()' for ALTER DATABASE ENCRYPT... command!
#  # There is bug in FB driver which leads this command to fail with 'token unknown' message
#  # The reason is that execute_immediate() silently set client dialect = 0 and any encryption statement
#  # can not be used for such value of client dialect.
#  # One need to to use only cursor_obj.execute() for encryption!
#  # See letter from Pavel Cisar, 20.01.20 10:36
#  ##############################################
#  cur.execute('alter database encrypt with %(PLUGIN_NAME)s key Red' % locals())
#  
#  con.commit()
#  time.sleep(2)
#  #          ^
#  #          +-------- !! ALLOW BACKGROUND ENCRYPTION PROCESS TO COMPLETE ITS JOB !!
#  
#  con.close()
#  
#  #-------------------------- shutdown temp DB and bring it online --------------------
#  
#  f_gfix_log = open( os.path.join(context['temp_directory'],'tmp_dbshut_6071.log'), 'w')
#  subprocess.call( [ context['gfix_path'], 'localhost:'+tmpfdb, "-sql_dialect", "1" ],
#                   stdout = f_gfix_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_gfix_log )
#  
#  #--------------------------- backup and restore --------------------------------------
#  fn_bkp_log=open( os.path.join(context['temp_directory'],'tmp_backup_6071.log'), 'w')
#  fn_bkp_err=open( os.path.join(context['temp_directory'],'tmp_backup_6071.err'), 'w')
#  
#  
#  subprocess.call([ context['gbak_path']
#                   ,"-b"
#                   ,"-v"
#                   ,"-KEYHOLDER", KHOLDER_NAME # "KeyHolder" | "fbSampleKeyHolder"
#                   ,"-crypt", PLUGIN_NAME.replace('"','') # DbCrypt | fbSampleDbCrypt
#                   ,'localhost:' + tmpfdb
#                   ,tmpbkp
#                  ],
#                  stdout=fn_bkp_log, stderr=fn_bkp_err)
#  
#  flush_and_close( fn_bkp_log )
#  flush_and_close( fn_bkp_err )
#  
#  
#  fn_res_log=open( os.path.join(context['temp_directory'],'tmp_restore_6071.log'), 'w')
#  fn_res_err=open( os.path.join(context['temp_directory'],'tmp_restore_6071.err'), 'w')
#  
#  # C:\\FB SS\\gbak.exe -rep -KEYHOLDER KeyHolder C:\\FBTESTING\\qa\\misc\\C6071.fbk /:C:\\FBTESTING\\qa\\misc\\c6071.restored.FDB
#  subprocess.call([ context['gbak_path']
#                   ,"-rep"
#                   ,"-v"
#                   ,"-KEYHOLDER", KHOLDER_NAME
#                   ,tmpbkp
#                   ,'localhost:' + tmpfdb
#                  ],
#                  stdout=fn_res_log, stderr=fn_res_err)
#  
#  flush_and_close( fn_res_log )
#  flush_and_close( fn_res_err )
#  
#  #-------------------------- validate just restored database --------------------
#  
#  f_valid_log = open( os.path.join(context['temp_directory'],'tmp_valid_6071.log'), 'w')
#  subprocess.call( [ context['gfix_path'], 'localhost:'+tmpfdb, "-v", "-full" ],
#                   stdout = f_valid_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_valid_log )
#  
#  #-----------------------------------------------
#  
#  # Check that all was fine:
#  
#  with open(f_gfix_log.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED GFIX OUTPUT: ' + line)
#  
#  with open(fn_bkp_err.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED BACKUP STDERR: ' + line)
#  
#  with open(fn_res_err.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED RESTORE STDERR: ' + line)
#  
#  with open(f_gfix_log.name,'r') as f:
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
#  # cleanup
#  ##########
#  time.sleep(1)
#  cleanup( ( f_gfix_log, fn_bkp_log, fn_bkp_err, fn_res_log, fn_res_err, f_valid_log, tmpfdb, tmpbkp ) )
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
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


