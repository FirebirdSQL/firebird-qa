#coding:utf-8
#
# id:           bugs.core_6246
# title:        Problem with too many number of columns in resultset.
# decription:   
#                   We create .sql with 32767 columns and run it with requirement to display SQLDA.
#                   All lines in produced output with 'charset: ' substring must contain only one value:
#                   * '3' for FB 3.x; '4' for FB 4.x.
#                   If some charset ID differs from expected, we raise error and terminate check furter lines.
#               
#                   Confirmed bug on 3.0.6.33272: first 32108 fields are shown in SQLDA with 'charset: 0 NONE'.
#                   String 'charset: 3 UNICODE_FSS' appeared only since 32109-th column and up to the end.
#               
#                   Checked on 3.0.6.33273 - works fine.
#                   Checked on 4.0.0.2353 -  works fine // 30.01.2021
#               
#                   Comment before 30-jan-2021:
#                   ---------------------------
#                   Attempt to run query with 32767 columns on 4.0 will raise:
#                       Statement failed, SQLSTATE = HY000
#                       request size limit exceeded
#                   Section for 4.0 intentionally contains temp message about missed implementation.
#                   Will be removed after fix CORE-6216 (see commet by Adriano in CORE-6246, date: 22/Mar/20 01:40 AM).
#                   ---------------------------
#                   30.01.2021: CORE-6212 was fixed. Section for 4.0 deleted; common code is used for 3.x and 4.x.
#                
# tracker_id:   CORE-6246
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
#  fb_major=db_conn.engine_version # type: double!
#  db_conn.close()
#  
#  MAX_FOR_PASS=32767
#  #MAX_FOR_PASS=32
#  
#  fld_list = ','.join( ('x1.rdb$field_name',) * MAX_FOR_PASS )
#  
#  # Create .sql with <MAX_FOR_PASS> columns:
#  ##########################################
#  sql_test='''
#  set sqlda_display on;
#  set planonly;
#  select
#      %(fld_list)s
#  from rdb$fields as x1 rows 1;
#  ''' % locals()
#  
#  f_pass_sql = open( os.path.join(context['temp_directory'],'tmp_6246_pass.sql'), 'w', buffering = 0)
#  f_pass_sql.write( sql_test )
#  f_pass_sql.close()
#  
#  f_pass_log = open( '.'.join( (os.path.splitext( f_pass_sql.name )[0], 'log') ), 'w', buffering = 0)
#  f_pass_err = open( '.'.join( (os.path.splitext( f_pass_sql.name )[0], 'err') ), 'w', buffering = 0)
#  
#  # This can take about 25-30 seconds:
#  ####################################
#  subprocess.call( [ context['isql_path'], dsn, '-q', '-i', f_pass_sql.name ], stdout = f_pass_log, stderr = f_pass_err)
#  
#  f_pass_log.close()
#  f_pass_err.close()
#  
#  # Checks:
#  #########
#  # 1. Result of STDERR must be empty:
#  with open(f_pass_err.name,'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED STDERR: '+line)
#  
#  # 1. For FB 3.x: only "charset: 3" must present in any string that describes column:
#  #     NN: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 93 charset:   3 UNICODE_FSS 
#  #                                                                           ^
#  #      0     1      2    3     4       5    6    7     8   9  10    11     12      13
#  # 2. For FB 4.x: only "charset: 4" must present in any string that describes column:
#  #     NN: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 252 charset:  4     UTF8
#  #                                                                           ^
#  #      0     1      2    3     4       5    6    7     8   9   10   11     12      13
#  #                                                                           ^
#  #                                                    we must check this token
#  #
#  # where 'NN:' is '01:', '02:', '03:', ... '32767:'
#  
#  ############## :::  N O T E  ::: #################
#  expected_charset_id = '3' if fb_major < 4 else '4'
#  ##################################################
#  
#  charset_id_position = -1
#  i=0
#  with open(f_pass_log.name,'r') as f:
#      for line in f:
#          i += 1
#          if 'sqltype:' in line:
#              if charset_id_position < 0:
#                 charset_id_position = [ (n,w) for n,w in enumerate( line.split() ) if w.lower() == 'charset:'.lower() ][0][0] + 1
#  
#              # charset_id = line.split()[-2]
#              charset_id = line.split()[ charset_id_position ]
#              if charset_id != expected_charset_id:
#                  print('At least one UNEXPECTED charset in SQLDA at position: %d. Line No: %d, charset_id: %s' % (charset_id_position, i, charset_id) )
#                  print(line)
#                  break
#  
#  if charset_id_position < 0:
#      # ISQL log is empty or not contains 'sqltype:' in any line.
#      print('UNEXPECTED RESULT: no lines with expected pattern found.')
#  
#  cleanup( [ i.name for i in ( f_pass_sql, f_pass_log, f_pass_err) ] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


