#coding:utf-8
#
# id:           bugs.core_6395
# title:        Allow usage of time zone displacement in config DefaultTimeZone
# decription:   
#                   We make backup of current firebird.conf for changing it two times:
#                   1. Add line with DefaultTimeZone = -7:00 and get local time by making *LOCAL* connect to current DB;
#                   2. Restore previous firebird.conf from its .bak-copy do second change: add line with DefaultTimeZone = 7:00.
#                      Then we run second local connect.
#               
#                   Each connect will ask FB to return CURRENT_TIME value (with casting it to '%H:%M:%S' format).
#                   Expected result: values must change from 1st to 2nd run for 14 hours (840 minutes).
#               
#                   ::: NB :::
#                   1. Affect of changed parameter DefaultTimeZone can be seen only if DB is attached using LOCAL protocol.
#                   2. FDB driver loads client library only *once* before this test launch and, in turn, this library reads firebird.conf.
#                      For this reason we have to launch separate (child) process two times, which will be forced to load firebird.conf
#                      every launch. This is why subprocess.call(['isql', ...]) is needed here rather than just query DB using cursor of
#                      pre-existing db_conn connection (see routine 'get_local_time').
#               
#                   Confirmed improvement on 4.0.0.2185.
#                   Value of time did not differ on previous builds (checked 4..0.2170).
#               
#                
# tracker_id:   CORE-6395
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
#  import sys
#  import os
#  import shutil
#  import socket
#  import getpass
#  import time
#  import datetime
#  from datetime import timedelta
#  import subprocess
#  from fdb import services
#  
#  db_name=db_conn.database_name
#  db_conn.close()
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
#      for f in f_names_list:
#         if type(f) == file:
#            del_name = f.name
#         elif type(f) == str:
#            del_name = f
#         else:
#            print('Unrecognized type of element:', f, ' - can not be treated as file.')
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#      
#  #--------------------------------------------
#  
#  def get_local_time( fb_home, db_name ):
#  
#      global flush_and_close
#      global subprocess
#      global cleanup
#  
#      sql_chk='select substring( cast(cast(current_time as time) as varchar(13)) from 1 for 8) from rdb$database'
#  
#      f_connect_sql = open( os.path.join(context['temp_directory'],'tmp_6396_check.sql'), 'w')
#      f_connect_sql.write('set heading off; ' + sql_chk + ';' )
#      flush_and_close( f_connect_sql )
#  
#      f_connect_log=open( os.path.join(context['temp_directory'],'tmp_6396_check.log'), 'w')
#      subprocess.call( [ context['isql_path'], db_name, "-i", f_connect_sql.name ], stdout=f_connect_log, stderr=subprocess.STDOUT )
#      flush_and_close( f_connect_log )
#  
#      changed_time = '00:00:00'
#      with open(f_connect_log.name,'r') as f:
#          for line in f:
#              if line.split():
#                  changed_time = line.strip()
#  
#      cleanup( [x.name for x in (f_connect_sql, f_connect_log)] )
#      return changed_time
#  
#  #---------------------------------------------
#  
#  svc = services.connect(host='localhost', user=user_name, password=user_password)
#  fb_home = svc.get_home_directory()
#  svc.close()
#  
#  dts = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
#  
#  fbconf_cur = os.path.join(fb_home, 'firebird.conf')
#  fbconf_bak = os.path.join(context['temp_directory'], 'firebird_'+dts+'.bak')
#  
#  shutil.copy2( fbconf_cur, fbconf_bak )
#  
#  f_fbconf=open( fbconf_cur, 'r')
#  fbconf_content=f_fbconf.readlines()
#  flush_and_close( f_fbconf )
#  
#  for i,s in enumerate( fbconf_content ):
#      line = s.lower().lstrip()
#      if line.startswith( 'DefaultTimeZone'.lower() ):
#          fbconf_content[i] = '# [temply commented] ' + s
#  
#  text2app='''
#  ### TEMPORARY CHANGED BY FBTEST FRAMEWORK ###
#  DefaultTimeZone = -7:00
#  ##############################################
#  '''
#  
#  f_fbconf=open( fbconf_cur, 'w')
#  f_fbconf.writelines( fbconf_content + [ '\\n' + x for x in text2app.split('\\n') ] )
#  flush_and_close( f_fbconf )
#  #..........................................
#  
#  changed_time1 = get_local_time( fb_home, db_name )
#  
#  # RESTORE previous content of firebird.conf. This must be done BEFORE drop mapping!
#  shutil.copy2( fbconf_bak, fbconf_cur )
#  
#  ##################################################
#  
#  text2app='''
#  ### TEMPORARY CHANGED BY FBTEST FRAMEWORK ###
#  DefaultTimeZone = +7:00
#  ##############################################
#  '''
#  
#  f_fbconf=open( fbconf_cur, 'w')
#  f_fbconf.writelines( fbconf_content + [ '\\n' + x for x in text2app.split('\\n') ] )
#  flush_and_close( f_fbconf )
#  
#  changed_time2 = get_local_time( fb_home, db_name )
#  
#  # RESTORE previous content of firebird.conf. This must be done BEFORE drop mapping!
#  shutil.move( fbconf_bak, fbconf_cur )
#  
#  print( (datetime.datetime.strptime(changed_time2, '%H:%M:%S') - datetime.datetime.strptime(changed_time1, '%H:%M:%S')).seconds // 60 )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    840
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


