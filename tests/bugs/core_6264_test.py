#coding:utf-8
#
# id:           bugs.core_6264
# title:        gbak with PIPE to stdout: invalid content if user '-se <host>:service_mgr' command switch
# decription:   
#                   NB: bug can be reproduced only if we create batch file and run it from Python using shell invocation,
#                   i.e. via subprocess.call(). Python builtin PIPE mechanism does not show any errors.
#                   For this reason, we create temp batch scenario, add necessary commands there and run it.
#                   Currently this scenario exists only for Windows. It will be implemented for POSIX later.
#               
#                   Confirmed bug on 3.0.6.33276, 4.0.0.1850.
#                   Works fine on 3.0.6.33277, 4.0.0.1854
#                
# tracker_id:   CORE-6264
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
#  import time
#  import subprocess
#  from subprocess import PIPE
#  from fdb import services
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  
#  #--------------------------------------------
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  fb_home = services.connect(host='localhost', user= user_name, password= user_password).get_home_directory()
#  this_db = db_conn.database_name
#  db_conn.close()
#  
#  tmp4restore=os.path.join(context['temp_directory'],'tmp_6264_check_restore.tmp')
#  
#  cleanup( (tmp4restore,) )
#  
#  
#  # BACKUP-RESTORE:
#  # C:\\FB SS\\gbak.exe -b -se localhost:service_mgr employee stdout | C:\\FB SS\\gbak -c stdin C:	emp\\employee.check-restore.tmp 
#  
#  fb_gbak = fb_home+'gbak'
#  fb_gfix = fb_home+'gfix'
#  txt = '''
#      @echo off
#      setlocal enabledelayedexpansion enableextensions
#      set ISC_USER=%(user_name)s
#      set ISC_PASSWORD=%(user_password)s
#      if exist %(tmp4restore)s del %(tmp4restore)s
#      if exist %(tmp4restore)s (
#          echo ### ERROR ###
#          echo Can not drop file %(tmp4restore)s
#      ) else (
#          %(fb_gbak)s -b -se localhost:service_mgr %(this_db)s stdout | %(fb_gbak)s -c stdin %(tmp4restore)s
#          if exist %(tmp4restore)s (
#              %(fb_gfix)s -v -full localhost:%(tmp4restore)s
#              %(fb_gfix)s -shut full -force 0 localhost:%(tmp4restore)s
#              del %(tmp4restore)s
#          )
#  
#      )
#  ''' %  dict(globals(), **locals())
#  
#  f_tmp_bat=open( os.path.join(context['temp_directory'],'tmp_run_6264.bat'), 'w', buffering = 0)
#  f_tmp_bat.write(txt)
#  f_tmp_bat.close()
#  
#  #####################
#  # DOES NOT WORK HERE:
#  #####################
#  # https://docs.python.org/2/library/subprocess.html#replacing-shell-pipeline
#  #p_sender = subprocess.Popen( [ fb_home+'gbak', '-b', '-se', 'localhost:service_mgr', this_db, 'stdout' ], stdout=PIPE)
#  #p_getter = subprocess.Popen( [ fb_home+'gbak', '-c', 'stdin',  tmp4restore ], stdin = p_sender.stdout, stdout = PIPE )
#  #p_sender.stdout.close()
#  #p_getter_stdout, p_getter_stderr = p_getter.communicate()
#  #print('p_getter_stdout:', p_getter_stdout) -- returns EMPTY string
#  #print('p_getter_stderr:', p_getter_stderr) -- returns None.
#  ######################
#  
#  f_bat_log=open( os.path.join(context['temp_directory'],'tmp_c6264.log'), "w", buffering = 0)
#  f_bat_err=open( os.path.join(context['temp_directory'],'tmp_c6264.err'), "w", buffering = 0)
#  
#  subprocess.call( [ f_tmp_bat.name ], stdout=f_bat_log, stderr=f_bat_err)
#  
#  f_bat_log.close()
#  f_bat_err.close()
#  
#  # Both STDOUT and STDERR results must be empty, which means no errors:
#  ########################
#  with open(f_bat_log.name, 'r') as f:
#      for line in f:
#          if line.split():
#              print( ''.join( ( 'UNEXPECTED STDOUT: ', line.strip() ) ) )
#  
#  with open(f_bat_err.name, 'r') as f:
#      for line in f:
#          if line.split():
#              print( ''.join( ( 'UNEXPECTED STDERR: ', line.strip() ) ) )
#  
#  cleanup( [ i.name for i in ( f_tmp_bat,f_bat_log,f_bat_err ) ] + [tmp4restore,] )
#  
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.6')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


