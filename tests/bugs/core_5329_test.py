#coding:utf-8
#
# id:           bugs.core_5329
# title:        Database gets partially corrupted in the "no-reserve" mode
# decription:   
#                  Test uses .fbk which was created on 2.5.7.
#                  We restore this database and run validation using gfix (NOT fbsvcmgr!).
#                  Validation should not produce any output and new lines in firebird.log should contain
#                  only messages about start and finish of validation with zero errors and warnings.
#               
#                  Confirmed bug on 4.0.0.326, 3.0.1.32573. No errors on 4.0.0.328,  3.0.1.32575
#                
# tracker_id:   CORE-5329
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = [('\t+', ' ')]

init_script_1 = """"""

db_1 = db_factory(from_backup='core5329.fbk', init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  import difflib
#  import re
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
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
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  def svc_get_fb_log( f_fb_log ):
#  
#    import subprocess
#  
#    subprocess.call([ context['fbsvcmgr_path'],
#                      "localhost:service_mgr",
#                      'action_get_fb_log'
#                    ],
#                    stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
#  
#  
#  # Get firebird.log content BEFORE running validation:
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_5329_fblog_before.txt'), 'w')
#  svc_get_fb_log( f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  # Only 'gfix -v' did show errors. 
#  #################################
#  # Online validation ('fbsvcmgr action_validate ...') worked WITHOUT any error/warningin its output.
#  
#  f_gfix_log=open( os.path.join(context['temp_directory'],'tmp_5329_gfix.txt'), 'w')
#  subprocess.call( [ context['gfix_path'], '-v', '-full', dsn], stdout=f_gfix_log, stderr=subprocess.STDOUT)
#  flush_and_close( f_gfix_log )
#  
#  # Get firebird.log content AFTER running validation:
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_5329_fblog_after.txt'), 'w')
#  svc_get_fb_log( f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  # Check-1. Log of 'gfix -v -full'should be EMPTY:
#  #################################################
#  
#  print("Checked_size of gfix stdlog+stderr: " + str(os.path.getsize(f_gfix_log.name)) )
#  
#  with open( f_gfix_log.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED VALIDATION LOG: '+line)
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_2668_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  pattern  = re.compile('.*VALIDATION.*|.*ERROR:.*')
#  
#  # NB: difflib.unified_diff() can show line(s) that present in both files, without marking that line(s) with "+". 
#  # Usually these are 1-2 lines that placed just BEFORE difference starts.
#  # So we have to check output before display diff content: lines that are really differ must start with "+".
#  
#  # Check-2. Difference betweenold and new firebird.log should contain 
#  # only lines about validation start and finish, without errors:
#  ###############################################################
#  
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+'):
#              if pattern.match(line.upper()):
#                  print( ' '.join(line.split()).upper() )
#  
#  
#  # Cleanup
#  #########
#  time.sleep(1)
#  cleanup( (f_gfix_log, f_fblog_before, f_fblog_after, f_diff_txt) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Checked_size of gfix stdlog+stderr: 0
    + VALIDATION STARTED
    + VALIDATION FINISHED: 0 ERRORS, 0 WARNINGS, 0 FIXED
  """

@pytest.mark.version('>=3.0.1')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


