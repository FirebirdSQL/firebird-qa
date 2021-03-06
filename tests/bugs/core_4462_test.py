#coding:utf-8
#
# id:           bugs.core_4462
# title:        Make it possible to restore compressed .nbk files without explicitly decompressing them
# decription:   
#                   Test uses three preliminarily created .zip files:
#                   1. 7zip-standalone-binary.zip -- contains standalone console utility 7za.exe
#                   2. zstd-standalone-binary.zip -- contains standalone console utility zstd.exe
#                   3. standard_sample_databases.zip  -- contains SQL statements for Firebird EMPLOYEE and Oracle "HR" schema.
#               
#                   We extract files from all of these .zip archives and do following:
#                   * apply Firebird SQL script which creates the same DB as standard EMPLOYEE;
#                   * invoke "nbackup -b 0 ..." and use Python PIPE mechanism for redirecting STDOUT to 7za.exe utility which,
#                     in turn, will accept data from this stream and compress them to .7z file.
#                     This eventually creates .7z file with compressed .nbk0 file.
#               
#                   * apply SQL script from Oracle "HR" schema which adds several other tables and data;
#                   * invoke "nbackup -b 1 ..." and use again Python PIPE mechanism for redirecting STDOUT to 7za.exe utility.
#                     This will create one more .7z file with compressed .nbk1 file.
#                   * invoke "nbackup -decompress ..." with specifying command for running 7za.exe which will extract every file
#                     from those which are specified in the command, i.e:
#               
#                     nbackup -decompress "c:\\path	oz.exe x -y" <fdb_for_restoring> <compressed_7z_with_nbk0> <compressed_7z_with_nbk1>
#               
#                   * validate just restored database and check content of firebird.log: it should NOT contain any errors or warnings.
#               
#                   ::: NB :::
#               
#                   This is *initial* implementation! We use trivial database with ascii-only metadata and data.
#                   Also, we use only 7za.exe compressor and zstd.exe is not yet used.
#               
#                   Later this test may be expanded for check non-ascii metadata and/or data.
#                   Checked on:
#                       4.0.0.1713 SS: 7.094s.
#                       4.0.0.1691 CS: 9.969s.
#                       3.0.5.33218 SS: 4.750s.
#                       3.0.5.33212 CS: 6.976s.
#                
# tracker_id:   CORE-4462
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import zipfile
#  import time
#  import re
#  import difflib
#  import subprocess
#  from subprocess import PIPE
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  #--------------------------------------------
#  
#  fb_home = services.connect(host='localhost', user= user_name, password= user_password).get_home_directory()
#  this_db = db_conn.database_name
#  
#  fdb_for_restore = os.path.join(context['temp_directory'],'tmp_4462_restored.fdb')
#  nbk0_name = '.'.join( (os.path.splitext( this_db )[0], 'nbk0') )
#  nbk1_name = '.'.join( (os.path.splitext( this_db )[0], 'nbk1') )
#  zip0_name = nbk0_name + '.7z'
#  zip1_name = nbk1_name + '.7z'
#  
#  f_list = ( fdb_for_restore, nbk0_name, nbk1_name, zip0_name, zip1_name )
#  cleanup( f_list )
#  
#  db_conn.close()
#  
#  for z in ( '7zip-standalone-binary.zip', 'zstd-standalone-binary.zip', 'standard_sample_databases.zip'):
#      zf = zipfile.ZipFile( os.path.join(context['files_location'], z ) )
#      zf.extractall( context['temp_directory'] )
#      zf.close()
#  # Result: scripts sample-DB_-_firebird.sql, sample-DB_-_oracle.sql and 
#  # standalone binaries for 7-zip and zstd have been extracted into context['temp_directory']
#  
#  p7z_exe = os.path.join(context['temp_directory'],'7za.exe')
#  zstd_exe = os.path.join(context['temp_directory'],'zstd.exe')
#  
#  ################################################################################################################
#  
#  f_sql_log=open( os.path.join(context['temp_directory'],'tmp_4462_init.log'), 'w', buffering = 0)
#  subprocess.call( [ fb_home + 'isql', dsn, '-i', os.path.join(context['temp_directory'],'sample-DB_-_firebird.sql') ], stdout = f_sql_log, stderr = subprocess.STDOUT)
#  f_sql_log.close()
#  
#  # https://docs.python.org/2/library/subprocess.html#replacing-shell-pipeline
#  #   output=`dmesg | grep hda`
#  #   becomes:
#  #   p1 = Popen(["dmesg"], stdout=PIPE)
#  #   p2 = Popen(["grep", "hda"], stdin=p1.stdout, stdout=PIPE)
#  #   p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
#  #   output = p2.communicate()[0]
#  
#  # nbackup.exe -b 0 employee stdout | 7za u -siemployee.nbk0 C:\\FBSS\\employee.nbk0.7z
#  
#  p_sender = subprocess.Popen( [ fb_home+'nbackup', '-b', '0', this_db, 'stdout' ], stdout=PIPE)
#  p_getter = subprocess.Popen( [ os.path.join(context['temp_directory'],'7za.exe'), 'u', '-bb3', '-bt', '-bse2', '-si' + os.path.split(nbk0_name)[1], zip0_name ], stdin = p_sender.stdout, stdout = PIPE )
#  p_sender.stdout.close()
#  p_getter_stdout, p_getter_stderr = p_getter.communicate()
#  
#  # result: file with name = %FBT_REPO%	mp\\BUGS.CORE_4462.nbk0.7z must be created at this point
#  
#  f_nbk0_to_7z_log = open( os.path.join(context['temp_directory'],'tmp_4462_nbk0_to_7z.log'), 'w', buffering = 0)
#  f_nbk0_to_7z_log.write( p_getter_stdout if p_getter_stdout else '' )
#  f_nbk0_to_7z_log.write( p_getter_stderr if p_getter_stderr else '' )
#  f_nbk0_to_7z_log.close()
#  
#  ################################################################################################################
#  
#  f_sql_log=open( os.path.join(context['temp_directory'],'tmp_4462_init.log'), 'a', buffering = 0)
#  subprocess.call( [ fb_home + 'isql', dsn, '-i', os.path.join(context['temp_directory'],'sample-DB_-_oracle.sql') ], stdout = f_sql_log, stderr = subprocess.STDOUT)
#  f_sql_log.close()
#  
#  p_sender = subprocess.Popen( [ fb_home+'nbackup', '-b', '1', this_db, 'stdout' ], stdout=PIPE)
#  p_getter = subprocess.Popen( [ os.path.join(context['temp_directory'],'7za.exe'), 'u', '-bb3', '-bt', '-bse2', '-si' + os.path.split(nbk1_name)[1], zip1_name ], stdin = p_sender.stdout, stdout = PIPE )
#  p_sender.stdout.close()
#  p_getter_stdout, p_getter_stderr = p_getter.communicate()
#  
#  # result: file with name = %FBT_REPO%	mp\\BUGS.CORE_4462.nbk1.7z must be created at this point
#  
#  
#  f_nbk1_to_7z_log = open( os.path.join(context['temp_directory'],'tmp_4462_nbk1_to_7z.log'), 'w', buffering = 0)
#  f_nbk1_to_7z_log.write( p_getter_stdout if p_getter_stdout else '' )
#  f_nbk1_to_7z_log.write( p_getter_stderr if p_getter_stderr else '' )
#  f_nbk1_to_7z_log.close()
#  
#  ################################################################################################################
#  
#  # Now we can restore database from compressed .7z files by invocation of nbackup with '-de[compress]' command key:
#  # nbackup -decompress "7za x -so" -r C:\\FBSS\\examples\\emp-restored\\employee-from-7z.fdb C:\\compressed_backup\\employee.nbk0.7z C:\\compressed_backup\\employee.nbk1.7z 
#  
#  f_restore_log=open( os.path.join(context['temp_directory'],'tmp_4462_nbackup_restore_from_7z.log'), 'w', buffering = 0)
#  subprocess.call( [ fb_home + 'nbackup', '-decompress', ' '.join( (p7z_exe,'x', '-y', '-so') ), '-r', fdb_for_restore, zip0_name, zip1_name ], stdout = f_restore_log, stderr = subprocess.STDOUT)
#  f_restore_log.close()
#  
#  
#  # Get firebird.log content BEFORE running validation:
#  #################################
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_4462_fblog_before.txt'), 'w', buffering = 0)
#  svc_get_fb_log( fb_home, f_fblog_before )
#  f_fblog_before.close()
#  
#  
#  # Run VALIDATION of just restored database:
#  ################
#  f_validation_log=open( os.path.join(context['temp_directory'],'tmp_4462_gfix_validate.log'), 'w', buffering = 0)
#  subprocess.call( [ fb_home + 'gfix', '-v', '-full', fdb_for_restore], stdout=f_validation_log, stderr=subprocess.STDOUT)
#  f_validation_log.close()
#  
#  
#  # Get firebird.log content AFTER running validation:
#  ################################
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_4462_fblog_after.txt'), 'w', buffering = 0)
#  svc_get_fb_log( fb_home, f_fblog_after )
#  f_fblog_after.close()
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
#  f_diff_fblog=open( os.path.join(context['temp_directory'],'tmp_4462_fblog_diff.txt'), 'w', buffering = 0)
#  f_diff_fblog.write(difftext)
#  f_diff_fblog.close()
#  
#  pattern  = re.compile('.*VALIDATION.*|.*ERROR:.*')
#  
#  # NB: difflib.unified_diff() can show line(s) that present in both files, without marking that line(s) with "+". 
#  # Usually these are 1-2 lines that placed just BEFORE difference starts.
#  # So we have to check output before display diff content: lines that are really differ must start with "+".
#  
#  # Check: difference between old and new firebird.log should contain 
#  # only lines about validation start and finish, without errors:
#  ###############################################################
#  
#  with open( f_diff_fblog.name,'r') as f:
#      for line in f:
#          if line.startswith('+'):
#              if pattern.match(line.upper()):
#                  print( ' '.join(line.split()).upper() )
#  
#  # Final checks:
#  ###############
#  # tmp_4462_gfix_validate.log tmp_4462_nbackup_restore_from_7z.log 
#  # Log for "nbackup -decompress -r ..." must be EMPTY:
#  with open( f_restore_log.name,'r') as f:
#      for line in f:
#          if line:
#              print('UNEXPECTED ERROR IN ' + f_restore_log.name + ': ' + line )
#  
#  # Log of "gfix -v -full" must be EMPTY (this means that no errors and no warning were found):
#  with open( f_validation_log.name,'r') as f:
#      for line in f:
#          if line:
#              print('UNEXPECTED ERROR IN ' + f_validation_log.name + ': ' + line )
#  
#  
#  f_list = [
#      fdb_for_restore
#      ,nbk0_name
#      ,nbk1_name
#      ,zip0_name
#      ,zip1_name
#      ,p7z_exe
#      ,zstd_exe
#      ,os.path.join(context['temp_directory'],'sample-DB_-_firebird.sql')
#      ,os.path.join(context['temp_directory'],'sample-DB_-_oracle.sql') 
#  ]
#  
#  f_list += [ i.name for i in (f_sql_log, f_nbk0_to_7z_log,f_nbk1_to_7z_log,f_restore_log,f_fblog_before,f_fblog_after,f_validation_log,f_diff_fblog) ]
#  
#  cleanup( f_list )
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    + VALIDATION STARTED
    + VALIDATION FINISHED: 0 ERRORS, 0 WARNINGS, 0 FIXED
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


