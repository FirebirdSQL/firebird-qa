#coding:utf-8
#
# id:           bugs.core_6348
# title:        Wire compression causes freezes
# decription:   
#                   Test does TWO measures related to speed of loading big blob into database:
#                       1) when WireCompression = true
#                       2) when WireCompression = false
#                   (see below usage of 'WIRE_COMPRESSION_VALUE' variable)
#                   Then we compare elapsed time (stored in milliseconds) between these two measures.
#               
#                   Time of loading when WireCompression = true will be greater than time for WireCompression = false.
#                   RATIO (i.e. <wc_ON> / <wc_OFF>) instead of absolute values is used as criteria for passing this test.
#                   This ratio must not exceed threshold that was defined beforehand
#                   I ran this test five times for each server mode, for FB 3.x and 4.x, both on Windows and Linux.
#               
#                   Results depend primarily on OS: about 3.05 for Windows and 1.48 for Linux.
#                   This difference looks strange and may be it is a good  idea to discussed this with FB developers.
#                   CURRENTLY threshold is set to approx. double value of maximal detected ratio (see 'MAX_RATIO_THRESHOLD').
#               
#                   NOTE-1
#                       Test temporary changes firebird.conf, so any abnormal termination of it can cause
#                       problems for other tests (which are to be executed after current).
#               
#                   NOTE-2
#                       EXTERNAL script for execution by Python is created here!
#                       Otherwise one can not reproduce problem described in the ticket if original firebird.conf
#                       We have to launch NEW (child) Python process which will run fully separately from current.
#               
#                   NOTE-3
#                       Test uses pre-created large binary file which can not be compressed: it is compressed trace log
#                       with original size about 2.2 Gb which was processed by 7-Zip with '-mx9 -mfb273' switches.
#               
#                   Confirmed bug on 4.0.0.1994: blob loading time is more than 120s.
#                   Checked on 4.0.0.2089.
#               
#               
#                   15.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                      Windows: 3.0.8.33445 SS/CS, 4.0.0.2422 SS/CS
#                      Linux:   3.0.8.33445 SS/CS, 4.0.0.2422 SS/CS
#               
#                
# tracker_id:   CORE-6348
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import subprocess
#  from subprocess import Popen
#  import datetime
#  import time
#  import shutil
#  from fdb import services
#  from datetime import datetime as dt
#  from datetime import timedelta
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  #############################
#  ###   T H R E S H O L D   ###
#  #############################
#  MAX_SECONDS_FOR_LOAD = 15
#  
#  db_conn.close()
#  
#  #-----------------------------------
#  def showtime():
#       global dt
#       return ''.join( (dt.now().strftime("%H:%M:%S.%f")[:11],'.') )
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
#  
#  FB_HOME = services.connect(host='localhost', user= user_name, password= user_password).get_home_directory()
#  # Resut: FB_HOME is full path to FB instance home (with trailing slash).
#  
#  if os.name == 'nt':
#      # For Windows we assume that client library is always in FB_HOME dir:
#      FB_CLNT=os.path.join(FB_HOME, 'fbclient.dll')
#  else:
#      # For Linux client library will be searched in 'lib' subdirectory of FB_HOME:
#      FB_CLNT=os.path.join(FB_HOME, 'lib', 'libfbclient.so' )
#  
#  
#  dts = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
#  
#  fbconf_cur = os.path.join( FB_HOME, 'firebird.conf')
#  fbconf_bak = os.path.join( FB_HOME, 'firebird'+dts+'.bak')
#  
#  shutil.copy2( fbconf_cur, fbconf_bak )
#  
#  blob_load_elapsed_time = {}
#  
#  for iter in (1,2):
#      # Restore original content of firebird.conf:
#      ##################
#      shutil.copy2( fbconf_bak, fbconf_cur )
#  
#      f_fbconf=open( fbconf_cur, 'r')
#      fbconf_content=f_fbconf.readlines()
#      f_fbconf.close()
#      for i,s in enumerate( fbconf_content ):
#          line = s.lower().lstrip()
#          if line.startswith( 'wirecompression'.lower() ):
#              fbconf_content[i] = '# [temply commented by fbtest for core_6348.fbt] ' + s
#  
#  
#      WIRE_COMPRESSION_VALUE = 'true' if iter == 1 else 'false'
#  
#      text2app=    '''
#      ### TEMPORARY CHANGED FOR CORE_6348.FBT ###
#      WireCompression = %(WIRE_COMPRESSION_VALUE)s
#      ##############################################
#      ''' % locals()
#  
#      fbconf_content += [ os.linesep + x for x in text2app.split( os.linesep ) ]
#  
#      f_fbconf=open( fbconf_cur, 'w', buffering = 0)
#      f_fbconf.writelines( fbconf_content )
#      flush_and_close( f_fbconf )
#  
#      
#      BLOB_FILE = os.path.join(context['files_location'],'core_6348.bin')
#  
#      external_python_code='''        from __future__ import print_function
#          from datetime import datetime as dt
#          from datetime import timedelta
#          import fdb
#          con = fdb.connect( dsn = r'%(dsn)s', user='%(user_name)s', password='%(user_password)s', fb_library_name = r'%(FB_CLNT)s' )
#          con.execute_immediate('recreate table test(b blob)')
#          con.commit()
#  
#          cur=con.cursor()
#          blob_src = r'%(BLOB_FILE)s'
#          blob_handle = open( blob_src, 'rb')
#  
#          da = dt.now()
#          cur.execute('insert into test(b) values(?)',[blob_handle])
#          db = dt.now()
#  
#          blob_handle.close()
#          diff_ms = (db-da).seconds*1000 + (db-da).microseconds//1000
#          print( str(diff_ms) )
#  
#          cur.close()
#          con.commit()
#          con.close()
#      ''' % dict(globals(), **locals())
#  
#      f_extern_py = open( os.path.join(context['temp_directory'],'tmp_6348.' + str(iter) + '.py'), 'w')
#      f_extern_py.write( '\\n'.join( [i.strip() for i in external_python_code.split('\\n')] ) )
#      flush_and_close( f_extern_py )
#      # f_extern_py.close()
#  
#      f_external_py_log = open( os.path.join(context['temp_directory'],'tmp_6348_py.' + str(iter) +  '.log' ), 'w')
#      subprocess.call( [sys.executable, f_extern_py.name], stdout = f_external_py_log, stderr = subprocess.STDOUT )
#      flush_and_close( f_external_py_log )
#  
#      with open(f_external_py_log.name,'r') as f:
#          blob_load_elapsed_time[ WIRE_COMPRESSION_VALUE ] = int(f.read().strip())
#      cleanup( ( f_extern_py, f_external_py_log ) )
#  
#  # Restore original content of firebird.conf:
#  ##################
#  shutil.move( fbconf_bak, fbconf_cur )
#  
#  #print(blob_load_elapsed_time)
#  #print( 1.00 * blob_load_elapsed_time['true'] / blob_load_elapsed_time['false'] )
#  
#  # 4.0.0.1994 SC:  {'false': 2036, 'true': 126711}, ratio: 62.24
#  # 4.0.0.2422 SS:  {'false': 831, 'true': 3722},    ratio:  4.48 // LINUX: 3.42; 3.11; 3.49; 3.44; 3.45
#  # 4.0.0.2422 CS:  {'false': 2088, 'true': 6903},   ratio:  3.31 // LINUX: 1.46; 1.46; 1.48; 1.46; 1.51
#  # 3.0.8.33445 SS: {'false': 1135, 'true': 3862},   ratio:  3.40 // LINUX: 1.52; 1.63; 1.52; 1.48; 1.51
#  # 3.0.8.33445 CS: {'false': 2160, 'true': 7675},   ratio:  3.55 // LINUX: 1.56; 1.61; 1.56; 1.55; 1.54
#  
#  ratio = 1.00 * blob_load_elapsed_time['true'] / blob_load_elapsed_time['false']
#  
#  if os.name == 'nt':
#      MAX_RATIO_THRESHOLD = 7
#  else:
#      MAX_RATIO_THRESHOLD = 20
#  #                         ^
#  #                         |
#  #                         |
#  #                ##################
#  #                ### THRESHOLD ####
#  #                ##################
#  
#  msg = 'Ratio is acceptable.'      if ratio < MAX_RATIO_THRESHOLD      else ( 
#              'Performance degradation when WireCompression = true is too high. ' +
#              'Without compression: %15.2f, with compression: %15.2f, ratio is %15.2f - more than max. threshold = %3d' % ( blob_load_elapsed_time['false'], blob_load_elapsed_time['true'], ratio, MAX_RATIO_THRESHOLD) 
#            )
#  
#  print(msg)
#  
#  # Cleanup
#  #########
#  time.sleep(1)
#  f_list=( f_extern_py, f_external_py_log )
#  cleanup( [ i.name for i in f_list ] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Ratio is acceptable.
  """

@pytest.mark.version('>=3.0.6')
@pytest.mark.xfail
def test_core_6348_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


