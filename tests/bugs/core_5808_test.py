#coding:utf-8
#
# id:           bugs.core_5808
# title:        Support backup of encrypted databases
# decription:   
#                   THIS TEST USES IBSurgeon Demo Encryption package
#                   ################################################
#                   ( https://ib-aid.com/download-demo-firebird-encryption-plugin/ ; https://ib-aid.com/download/crypt/CryptTest.zip )
#                   License file plugins\\dbcrypt.conf with unlimited expiration was provided by IBSurgeon to Firebird Foundation (FF).
#                   This file was preliminary stored in FF Test machine.
#                   Test assumes that this file and all neccessary libraries already were stored into FB_HOME and %FB_HOME%\\plugins.
#               
#                   After test database will be created, we try to encrypt it using 'alter database encrypt with <plugin_name> ...' command
#                   (where <plugin_name> = dbcrypt - name of .dll in FB_HOME\\plugins\\ folder that implements encryption).
#                   Then we allow engine to complete this job - take delay about 1..2 seconds BEFORE detach from database.
#                   After this we make  backup of encrypted database + restore.
#               
#                   Then we make snapshot of firebird.log, run 'gfix -v -full' of restored database and once again take snapshot of firebird.log.
#                   Comparison of these two logs is result of validation. It should contain line about start and line with finish info.
#                   The latter must look like this: "Validation finished: 0 errors, 0 warnings, 0 fixed"
#               
#                   Checked on:
#                       40sS, build 4.0.0.1487: OK, 6.552s.
#                       40sC, build 4.0.0.1421: OK, 11.812s.
#                       40Cs, build 4.0.0.1485: OK, 8.097s.
#               
#                   15.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 4.0.0.2416
#                     Linux:   4.0.0.2416
#                
# tracker_id:   CORE-5808
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
# 
#  import os
#  import time
#  import difflib
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
#  def svc_get_fb_log( f_fb_log ):
#  
#    global subprocess
#  
#    subprocess.call( [ context['fbsvcmgr_path'],
#                       "localhost:service_mgr",
#                       "action_get_fb_log"
#                     ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
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
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_5808.fdb'
#  tmpfbk='$(DATABASE_LOCATION)'+'tmp_core_5808.fbk'
#  
#  f_list=( tmpfdb, tmpfbk )
#  cleanup( f_list )
#  
#  
#  # 14.04.2021.
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else '"fbSampleDbCrypt"'
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb )
#  cur = con.cursor()
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
#  
#  time.sleep(2)
#  #          ^
#  #          +-------- !! ALLOW BACKGROUND ENCRYPTION PROCESS TO COMPLETE ITS JOB !!
#  
#  con.close()
#  
#  f_backup_log = open( os.path.join(context['temp_directory'],'tmp_backup_5808.log'), 'w')
#  f_backup_err = open( os.path.join(context['temp_directory'],'tmp_backup_5808.err'), 'w')
#  
#  subprocess.call( [ context['gbak_path'], "-v", "-b", 'localhost:' + tmpfdb, tmpfbk],
#                   stdout = f_backup_log,
#                   stderr = f_backup_err
#                 )
#  flush_and_close( f_backup_log )
#  flush_and_close( f_backup_err )
#  
#  
#  f_restore_log = open( os.path.join(context['temp_directory'],'tmp_restore_5808.log'), 'w')
#  f_restore_err = open( os.path.join(context['temp_directory'],'tmp_restore_5808.err'), 'w')
#  
#  subprocess.call( [ context['gbak_path'], "-v", "-rep", tmpfbk, 'localhost:'+tmpfdb],
#                   stdout = f_restore_log,
#                   stderr = f_restore_err
#                 )
#  flush_and_close( f_restore_log )
#  flush_and_close( f_restore_err )
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_5808_fblog_before.txt'), 'w')
#  svc_get_fb_log( f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  
#  f_validate_log = open( os.path.join(context['temp_directory'],'tmp_validate_5808.log'), 'w')
#  f_validate_err = open( os.path.join(context['temp_directory'],'tmp_validate_5808.err'), 'w')
#  
#  subprocess.call( [ context['gfix_path'], "-v", "-full", tmpfdb ],
#                   stdout = f_validate_log,
#                   stderr = f_validate_err
#                 )
#  flush_and_close( f_validate_log )
#  flush_and_close( f_validate_err )
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_5808_fblog_after.txt'), 'w')
#  svc_get_fb_log( f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  
#  # Compare firebird.log versions BEFORE and AFTER this test:
#  ######################
#  
#  oldfb=open(f_fblog_before.name, 'r')
#  newfb=open(f_fblog_after.name, 'r')
#  
#  difftext = ''.join(difflib.unified_diff(
#      oldfb.readlines(), 
#      newfb.readlines()
#    ))
#  oldfb.close()
#  newfb.close()
#  
#  
#  with open( f_backup_err.name,'r') as f:
#      for line in f:
#          print("UNEXPECTED PROBLEM ON BACKUP, STDERR: "+line)
#  
#  with open( f_restore_err.name,'r') as f:
#      for line in f:
#          print("UNEXPECTED PROBLEM ON RESTORE, STDERR: "+line)
#  
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_5808_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  allowed_patterns = (
#        re.compile( '\\+\\s+Validation\\s+started', re.IGNORECASE)
#       ,re.compile( '\\+\\s+Validation\\s+finished:\\s+0\\s+errors,\\s+0\\s+warnings,\\s+0\\s+fixed', re.IGNORECASE)
#  )
#  
#  
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          match2some = filter( None, [ p.search(line) for p in allowed_patterns ] )
#          if match2some:
#              print( (' '.join( line.split()).upper() ) )
#  
#  # CLEANUP:
#  ##########
#  # do NOT remove this pause otherwise some of logs will not be enable for deletion and test will finish with 
#  # Exception raised while executing Python test script. exception: WindowsError: 32
#  time.sleep(1)
#  cleanup( (f_backup_log, f_backup_err, f_restore_log, f_restore_err, f_validate_log, f_validate_err, f_fblog_before, f_fblog_after, f_diff_txt, tmpfdb, tmpfbk) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    + VALIDATION STARTED
    + VALIDATION FINISHED: 0 ERRORS, 0 WARNINGS, 0 FIXED
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


