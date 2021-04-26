#coding:utf-8
#
# id:           bugs.core_6348
# title:        Wire compression causes freezes
# decription:   
#                  We create copy of %FIREBIRD_HOME%
#               irebird.conf and change it content by adding line:
#                      WireCompression = true
#               
#                  Then we use pre-created large binary file which can not be compressed (it is .7z) and
#                  check how long it is loaded into blob field of test table.
#                  
#                  ::: NOTE :::
#                  EXTERNAL script for execution by Python is created here!
#                  Otherwise one can not reproduce problem described in the ticket if original firebird.conf
#                  does NOT contain 'WireCompression' or its value is set to false.
#                  We have to launch NEW (child) Python process which will run fully separately from current.
#               
#                  Dozen measures show that after this CORE was fixed, blob is loaded for less 5 seconds
#                  on usual PC with HDD/ram=12gb/CPU 3.07 MHz.
#               
#                  It was decided to use THRESHOLD about 15 seconds to make conclusion that all remains fine.
#                  May be this threshold needs to be sometime revised.
#                  
#                  Confirmed bug on 4.0.0.1994: blob loading time is more than 120s.
#                  Checked on 4.0.0.2089 -- all fine, blob is loaded for less than 5s.
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
# 
#  import os
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
#  #-----------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      os.fsync(file_handle.fileno())
#  
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  #--------------------------------------------
#  
#  
#  fb_home = services.connect(host='localhost', user= user_name, password= user_password).get_home_directory()
#  # Resut: fb_home is full path to FB instance home (with trailing slash).
#  
#  dts = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
#  
#  fbconf_cur = os.path.join( fb_home, 'firebird.conf')
#  fbconf_bak = os.path.join( fb_home, 'firebird'+dts+'.bak')
#  
#  shutil.copy2( fb_home+'firebird.conf', fbconf_bak )
#  
#  f_fbconf=open( fbconf_cur, 'r')
#  fbconf_content=f_fbconf.readlines()
#  f_fbconf.close()
#  for i,s in enumerate( fbconf_content ):
#      line = s.lower().lstrip()
#      if line.startswith( 'wirecompression'.lower() ):
#          fbconf_content[i] = '# [temply commented by fbtest for core_6348.fbt] ' + s
#  
#  
#  text2app='''
#  ### TEMPORARY CHANGED FOR CORE_6348.FBT ###
#  WireCompression = true
#  ##############################################
#  '''
#  
#  fbconf_content += [ os.linesep + x for x in text2app.split( os.linesep ) ]
#  
#  f_fbconf=open( fbconf_cur, 'w', buffering = 0)
#  f_fbconf.writelines( fbconf_content )
#  flush_and_close( f_fbconf )
#  
#  FB_CLNT = os.path.join(fb_home, 'fbclient.dll')
#  BLOB_FILE = os.path.join(context['files_location'],'core_6348.bin')
#  
#  external_python_code='''from __future__ import print_function
#  from datetime import datetime as dt
#  from datetime import timedelta
#  import fdb
#  con = fdb.connect( dsn = r'%(dsn)s', user='%(user_name)s', password='%(user_password)s', fb_library_name = r'%(FB_CLNT)s' )
#  con.execute_immediate('create table test(b blob)')
#  con.commit()
#  
#  cur=con.cursor()
#  blob_src = r'%(BLOB_FILE)s'
#  blob_handle = open( blob_src, 'rb')
#  
#  da=dt.now()
#  cur.execute('insert into test(b) values(?)',[blob_handle])
#  db=dt.now()
#  
#  blob_handle.close()
#  diff=db-da
#  print( 'Acceptable' if diff.seconds < %(MAX_SECONDS_FOR_LOAD)s else 'BLOB LOADED TOO SLOW: ' + str(diff.seconds) + 's, THRESHOLD IS: ' + str(%(MAX_SECONDS_FOR_LOAD)s)+'s' )
#  
#  cur.close()
#  con.commit()
#  con.close()
#  ''' % dict(globals(), **locals())
#  
#  f_extern_py=open( os.path.join(context['temp_directory'],'tmp_6348.py'), 'w')
#  f_extern_py.write(external_python_code)
#  flush_and_close( f_extern_py )
#  
#  f_external_py_log = open( os.path.join(context['temp_directory'],'tmp_6348.log'), 'w')
#  subprocess.call( [sys.executable, f_extern_py.name], stdout = f_external_py_log, stderr = subprocess.STDOUT )
#  flush_and_close( f_external_py_log )
#  
#  # Restore original content of firebird.conf:
#  ##################
#  shutil.copy2( fbconf_bak, fb_home+'firebird.conf' )
#  os.remove( fbconf_bak )
#  
#  with open(f_external_py_log.name, 'r') as f:
#      for line in f:
#          print(line)
#  
#  time.sleep(1)
#  
#  # Cleanup
#  #########
#  f_list=( f_extern_py, f_external_py_log )
#  cleanup( [ i.name for i in f_list ] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Acceptable
  """

@pytest.mark.version('>=3.0.6')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_6348_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


