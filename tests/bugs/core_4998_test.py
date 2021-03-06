#coding:utf-8
#
# id:           bugs.core_4998
# title:        Both client and server could not close connection after failed authentification
# decription:   
#                   Reproduced on 3.0.0.32136 RC1 with firebird.conf:
#                       AuthServer = Legacy_Auth,Srp
#                       AuthClient = Srp,Legacy_Auth
#                   ::: NB-1 ::: 
#                   In order to get this environment for client test temp-ly CHANGES firebird.conf
#                   Test will restore original firebird.conf in the end.
#               
#                   ::: NB-2 ::: 
#                   We have to prepare auxiliary Python script to be executed in SEPARATE (NEW!) execution context,
#                   otherwise firebird.log is filled with messages "errno = 10054" only after this test completely finished.
#                   See variable 'f_python_separate_exec_context' - it points to this temp .py file.
#                   This aux Python script is called like this:
#                       os.system( f_python_separate_exec_context )
#               
#                   It contains three attempts to make connection with invalid passwords. 
#                   Exceptions ('Your user/password not defined...') are suppressed, we need only make these attempts to check
#                   that no new records withh be added to firebird.log (as it is confirmed to be in 3.0.0.32136 RC1).
#                   
#                   File firebird.log is compared BEFORE and AFTER os.system( f_python_separate_exec_context ).
#                   No new messages related to 10054 error should occur during this test in firebird.log.
#               
#                   3.0.0.32366 RC2 - works OK.
#               
#                   Also checked on:
#                       30Cs, build 3.0.4.32972: OK, 6.172s.
#                       30SS, build 3.0.4.32972: OK, 4.375s.
#                       40CS, build 4.0.0.955: OK, 7.281s.
#                       40SS, build 4.0.0.977: OK, 4.704s.
#                
# tracker_id:   CORE-4998
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
# import os
#  import sys
#  import subprocess
#  import difflib
#  import datetime
#  import time
#  import re
#  import shutil
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  THIS_DSN = dsn
#  DBAUSR = user_name
#  db_conn.close()
#  
#  svc = services.connect(host='localhost')
#  fb_home=svc.get_home_directory()
#  svc.close()
#  
#  #--------------------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb'):
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
#  ###########################################################################################
#  
#  dts = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
#  
#  fbconf = os.path.join( fb_home, 'firebird.conf')
#  fbcbak = os.path.join( fb_home, 'firebird_'+dts+'.bak')
#  
#  shutil.copy2( fbconf, fbcbak )
#  
#  f_fbconf = open(fbconf,'r')
#  fbconf_content=f_fbconf.readlines()
#  f_fbconf.close()
#  
#  for i,s in enumerate( fbconf_content ):
#      if s.lower().lstrip().startswith( 'wirecrypt'.lower() ):
#          fbconf_content[i] = '# <temply commented> ' + s
#      if s.lower().lstrip().startswith( 'AuthClient'.lower() ):
#          fbconf_content[i] = '# <temply commented> ' + s
#  
#  fbconf_content.append('\\n# Temporarily added by fbtest, CORE-4998. Should be removed auto:')
#  fbconf_content.append("\\n#" + '='*30 )
#  fbconf_content.append('\\nAuthClient = Srp,Legacy_Auth')
#  fbconf_content.append("\\n#" + '='*30 )
#  
#  f_fbconf=open(fbconf,'w')
#  f_fbconf.writelines( fbconf_content )
#  flush_and_close( f_fbconf )
#  
#  ###########################################################################################
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_4998_fblog_before.txt'), 'w')
#  svc_get_fb_log( f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  other_exec_context_python_text = '''import fdb
#  
#  for i in range(0,3):
#      con1 = None
#      try:
#          con1 = fdb.connect( dsn = '%(THIS_DSN)s', user = '%(DBAUSR)s', password = 'inv@l1d' + str(i) )
#      except Exception, e:
#          pass
#      finally:
#          if con1:
#              con1.close()
#  exit(0)
#  ''' % locals()
#  
#  f_python_separate_exec_context = os.path.join(context['temp_directory'], 'tmp_core_4998_try_connect_with_invalid_passwords.py')
#  
#  f = open( f_python_separate_exec_context, 'w')
#  f.write( other_exec_context_python_text )
#  flush_and_close( f )
#  
#  ########################################################################################################
#  ###    l a u n c h     P y t h o n    i n    a n o t h e r    e x e c u t i o n     c o n t e x t    ###
#  ########################################################################################################
#  
#  # 17.06.2018. We have to add full path and name of interpretep (e.g. 'C:\\Python27\\python.exe')
#  # because it can appear that OS will not be able to recognize how to handle .py files!
#  # sys.executable - returns full path to Python exe, 
#  
#  os.system( sys.executable + ' ' + f_python_separate_exec_context )
#  
#  time.sleep(1)
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_4998_fblog_after.txt'), 'w')
#  svc_get_fb_log( f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  # RESTORE original config:
#  ##########################
#  shutil.move( fbcbak, fbconf)
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_4998_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  # INET/inet_error: read errno = 10054
#  
#  allowed_patterns = (
#       re.compile('\\.*inet_error\\:{0,1}\\s{0,}read\\s+errno\\s{0,}\\={0,}\\s{0,}10054\\.*', re.IGNORECASE),
#  )
#  
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+'):
#              match2some = filter( None, [ p.search(line) for p in allowed_patterns ] )
#              if match2some:
#                  print( 'UNEXPECTED TEXT IN FIREBIRD.LOG: ' + (' '.join(line.split()).upper()) )
#  
#  #####################################################################
#  # Cleanup:
#  time.sleep(1)
#  cleanup( (f_diff_txt,f_fblog_before,f_fblog_after, f_python_separate_exec_context) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


