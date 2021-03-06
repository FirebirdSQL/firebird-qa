#coding:utf-8
#
# id:           bugs.core_4760
# title:        Can not create user with non-ascii (multi-byte) characters in it's name
# decription:   
#                   User with name Εὐκλείδης ('Euclid') encoded in UTF8 is used in this test.
#               
#                   NB-1: connection is made using FDB connect() method: ISQL (and also its CONNECT statement) has
#                   problems when trying to use non-ascii names.
#                   NB-2: separate SQL script is generated for DROP this user.
#               
#                   Checked on: 4.0.0.2416 (Windows and Linux)
#                 
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         bugs.core_4760

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[\t ]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import io
#  import subprocess
#  import time
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
#            print('type(f_names_list[i])=',type(f_names_list[i]))
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  sql_txt='''    set bail on;
#      set names utf8;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#  
#      create or alter user "Εὐκλείδης" password '123' using plugin Srp;
#  ''' % dict(globals(), **locals())
#  
#  f_ddl_sql = open( os.path.join(context['temp_directory'], 'tmp_4760_utf8_ddl.sql'), 'w' )
#  f_ddl_sql.write( sql_txt )
#  flush_and_close( f_ddl_sql )
#  
#  f_ddl_log = open( os.path.splitext(f_ddl_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_ddl_sql.name ],
#                   stdout = f_ddl_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_ddl_log )
#  
#  with io.open(f_ddl_log.name, 'r', encoding='utf8' ) as f:
#      result_log = f.readlines()
#  
#  for i in result_log:
#      print( i.encode('utf8') ) # do not miss '.encode()' here, otherwise get: "ordinal not in range(128)"
#  
#  f_run_log = io.open( os.path.join(context['temp_directory'], 'tmp_4760_utf8_run.log'), 'w', encoding = 'utf8' )
#  
#  con = fdb.connect(dsn = dsn, user = "Εὐκλείδης", password = '123', charset = 'utf8', utf8params = True)
#  cur = con.cursor()
#  cur.execute('select m.mon$user from mon$attachments m where m.mon$attachment_id = current_connection')
#  col = cur.description
#  for r in cur:
#      for i in range(0,len(col)):
#          f_run_log.write( ' '.join((col[i][0],':',r[i], '\\n')) )
#  
#  cur.close()
#  con.close()
#  flush_and_close(f_run_log)
#  
#  # Generate SQL script for DROP non-ascii user.
#  ##############################################
#  sql_txt='''
#      set bail on;
#      set names utf8;
#      set list on;
#      -- set echo on;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#      select count(*) non_ascii_user_before_drop from sec$users where sec$user_name ='Εὐκλείδης';
#      drop user "Εὐκλείδης" using plugin Srp;
#      commit;
#      select count(*) non_ascii_user_after_drop from sec$users where sec$user_name ='Εὐκλείδης';
#  ''' % dict(globals(), **locals())
#  
#  f_drop_sql = open( os.path.join(context['temp_directory'], 'tmp_4760_utf8_drop.sql'), 'w' )
#  f_drop_sql.write(  sql_txt )
#  flush_and_close( f_drop_sql )
#  
#  f_drop_log = open( os.path.splitext(f_drop_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_drop_sql.name ],
#                   stdout = f_drop_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_drop_log )
#  
#  with io.open(f_run_log.name, 'r', encoding='utf8' ) as f:
#      result_in_utf8 = f.readlines()
#  
#  
#  for i in result_in_utf8:
#      print( i.encode('utf8') )
#  
#  with open(f_drop_log.name,'r') as f:
#      for line in f:
#          print(line)
#  
#  # cleanup:
#  ###########
#  time.sleep(2)
#  
#  # DO NOT use here: cleanup( (f_ddl_sql, f_ddl_log, f_drop_sql, f_drop_log, f_run_log) ) -- 
#  # Unrecognized type of element: <closed file 'C:\\FBTESTING\\qa\\fbt-repo\\tmp\\tmp_4760_utf8_run.log', mode 'wb' at 0x0000000005A20780> - can not be treated as file.
#  # type(f_names_list[i])= <type 'instance'>Traceback (most recent call last):
#  
#  cleanup( [i.name for i in (f_ddl_sql, f_ddl_log, f_drop_sql, f_drop_log, f_run_log)] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MON$USER : Εὐκλείδης
    NON_ASCII_USER_BEFORE_DROP 1
    NON_ASCII_USER_AFTER_DROP 0
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


