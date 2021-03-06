#coding:utf-8
#
# id:           bugs.core_5618
# title:        Part of the pages of the second level blobs is not released when deleting relations.
# decription:   
#                   We create table with blob field and write into it binary data with length that 
#                   is too big to store such blob as level-0 and level-1. Filling is implemented as
#                   specified in:
#                       http://pythonhosted.org/fdb/differences-from-kdb.html#stream-blobs
#                   Then we drop table and close connection.
#                   Finally, we obtain firebird.log, run full validation (like 'gfix -v -full' does) and get firebird.log again.
#                   Comparison of two firebird.log versions should give only one difference related to warnings, and they count 
#                   must be equal to 0.
#               
#                   Reproduced on 3.0.3.32837, got lot of warnings in firebird.log when did usual validation ('gfix -v -full ...')
#                   Checked on:
#                       30SS, build 3.0.3.32856: OK, 4.047s.
#                       40SS, build 4.0.0.834: OK, 8.266s.
#                
# tracker_id:   CORE-5618
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """
      recreate table test(b blob sub_type 0);
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import zipfile
#  import difflib
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  this_fdb = db_conn.database_name
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
#                      "action_get_fb_log"
#                    ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
#  
#  
#  #####################################################################
#  # Move database to FW = OFF in order to increase speed of insertions and output its header info:
#  
#  fwoff_log=open( os.path.join(context['temp_directory'],'tmp_fw_off_5618.log'), 'w')
#  subprocess.call( [ context['fbsvcmgr_path'], "localhost:service_mgr",
#                     "action_properties",
#                     "prp_write_mode", "prp_wm_async",
#                     "dbname", this_fdb
#                   ],
#                   stdout=fwoff_log, 
#                   stderr=subprocess.STDOUT
#                 )
#  flush_and_close( fwoff_log )
#  
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_5618.zip') )
#  blob_src = 'core_5618.bin'
#  zf.extract( blob_src, '$(DATABASE_LOCATION)')
#  zf.close()
#  
#  con1 = fdb.connect(dsn = dsn)
#  
#  cur1=con1.cursor()
#  blob_src = ''.join( ('$(DATABASE_LOCATION)', blob_src) )
#  
#  blob_handle = open( blob_src, 'rb')
#  cur1.execute('insert into test(b) values(?)',[blob_handle])
#  blob_handle.close()
#  
#  cur1.close()
#  con1.execute_immediate('drop table test');
#  con1.commit()
#  con1.close()
#  
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_4337_fblog_before.txt'), 'w')
#  svc_get_fb_log( f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  
#  ##########################################################
#  # Run full validation (this is what 'gfix -v -full' does):
#  
#  val_log=open( os.path.join(context['temp_directory'],'tmp_onval_5618.log'), 'w')
#  
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_repair", 
#                    "rpr_validate_db",
#                    "rpr_full",
#                    "dbname", this_fdb
#                   ],
#                   stdout=val_log, 
#                   stderr=subprocess.STDOUT
#                 )
#  
#  flush_and_close( val_log )
#  
#  
#  # Get content of firebird.log AFTER test finish.
#  #############################
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_4337_fblog_after.txt'), 'w')
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_4337_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+') and 'warning'.upper() in line.upper():
#                  print( 'DIFF IN FIREBIRD.LOG: ' + (' '.join(line.split()).upper()) )
#  
#  with open( fwoff_log.name,'r') as f:
#      for line in f:
#          print(  ''.join( ('Unexpected line in ', fwoff_log.name, ':', line ) ) )
#  
#  with open( val_log.name,'r') as f:
#      for line in f:
#          print(  ''.join( ('Unexpected line in ', val_log.name, ':', line ) ) )
#  
#  
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_fblog_before, f_fblog_after, f_diff_txt, val_log, blob_handle, fwoff_log) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DIFF IN FIREBIRD.LOG: + VALIDATION FINISHED: 0 ERRORS, 0 WARNINGS, 0 FIXED
  """

@pytest.mark.version('>=3.0.3')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


