#coding:utf-8
#
# id:           bugs.core_6262
# title:        SHOW DOMAIN/TABLE does not display character set of system objects
# decription:   
#                   We gather all system domains which belongs to TEXT family by query to rdb$fields.
#                   Then for each record from its resulset we issue statement: 'SHOW DOMAIN ... ;'
#                   and write it to .SQL file. After all records will be processed, we run ISQL and
#                   perform this script. Every row from its output must contain phrase 'CHARACTER SET'.
#               
#                   Checked on 4.0.0.1803.
#               
#                   ::: NB ::: additional filtering: "where f.rdb$character_set_id > 1" is needed when
#                   we query rdb$fields. Otherwise we get some domains without 'CHARACTER SET' phrases
#                   domains definition:
#                       rdb$character_set_id=0:
#                           show domain RDB$EDIT_STRING;
#                           RDB$EDIT_STRING                 VARCHAR(127) Nullable
#                           show domain RDB$MESSAGE;
#                           RDB$MESSAGE                     VARCHAR(1023) Nullable
#                       rdb$character_set_id=1:
#                           RDB$SYSTEM_PRIVILEGES           BINARY(8) Nullable
#                
# tracker_id:   CORE-6262
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import time
#  import subprocess
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_6262_chk.sql'), 'w')
#  
#  cur = db_conn.cursor()
#  sql='''
#      select 'show domain '|| trim(f.rdb$field_name) ||';' as show_expr
#      from rdb$fields f
#      where f.rdb$character_set_id > 1
#      order by f.rdb$field_name
#  '''
#  
#  cur.execute(sql)
#  text_domains_count = 0
#  for r in cur:
#      f_sql_chk.write( r[0]+os.linesep )
#      text_domains_count += 1
#  
#  flush_and_close( f_sql_chk )
#  db_conn.close()
#  
#  
#  f_sql_log = open( ''.join( (os.path.splitext(f_sql_chk.name)[0], '.log' ) ), 'w')
#  f_sql_err = open( ''.join( (os.path.splitext(f_sql_log.name)[0], '.err' ) ), 'w')
#  
#  subprocess.call( [ context['isql_path'], dsn, '-i', f_sql_chk.name ], stdout = f_sql_log, stderr = f_sql_err)
#  
#  flush_and_close( f_sql_log )
#  flush_and_close( f_sql_err )
#  
#  # Checks:
#  #########
#  # 1. Result of STDERR must be empty:
#  with open(f_sql_err.name,'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED STDERR: '+line)
#  
#  # 2. All <text_domains_count> lines in STDOUT have to contain phrase 'CHARACTER SET':
#  
#  lines_with_charset, lines_without_charset = 0, 0
#  
#  with open(f_sql_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              if 'CHARACTER SET' in line:
#                  lines_with_charset += 1
#              else:
#                  lines_without_charset += 1
#  
#  if lines_with_charset > 0:
#      print('Number of lines with specified charset: '  + ( 'SAME AS' if lines_with_charset == text_domains_count else str(lines_with_charset)+' - LESS THEN' ) + ' NUMBER OF TEXT DOMAINS' )
#  else:
#      print('SOMETHING WAS WRONG: COULD NOT FIND ANY LINE WITH "CHARACTER SET" PHRASE')
#  
#  print('Number of lines with missed charset:',lines_without_charset)
#  
#  # cleanup
#  #########
#  time.sleep(1)
#  cleanup( (f_sql_chk, f_sql_log, f_sql_err ) )
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Number of lines with specified charset: SAME AS NUMBER OF TEXT DOMAINS
    Number of lines with missed charset: 0
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


