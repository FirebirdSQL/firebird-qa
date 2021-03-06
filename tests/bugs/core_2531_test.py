#coding:utf-8
#
# id:           bugs.core_2531
# title:        The famous "cannot transliterate" error may be thrown when selecting data from the monitoring tables
# decription:   
#                  In order to check issues of ticket we have to create Python script which is encoded in non-ascii codepage and also
#                  its codepage should be NON utf8 (choosed: Windows 1252). This is because all .fbt files have to be encoded only in UTF8,
#                  so we can not put inside .fbt a statement which contains non-ascii SINGLE-BYTE characters.
#                  
#                  Character |å|, "LATIN SMALL LETTER A WITH RING ABOVE",  was selected in order to verify ticket issue, see:
#                  http://www.fileformat.info/info/unicode/char/00e5/index.htm
#                  
#                  Temporary Python file ("tmp_2531_run.py") will contain encoding statement ('# coding: latin-1') followed by commands for:
#                  1) make first attachment to database, by Python itself, with charset = Win1252, with preparing: "select 'gång' from rdb$database";
#                     also, this attachments SAVES string of this query into table (NOTE: it works with charset = win1252);
#                  2) make second attachment by ISQL, with charset = utf8, which will query mon$statements.mon$sql_text - this should return query
#                     which has been prepared by first attachment. This query is compared to that which was stored into table by attachment-1,
#                     and these rows should be equal: |select 'gång' from rdb$database|
#                  
#                  Confirmed wrong (incompleted) output of mon$sql_text on 2.1.0.17798 (but there is no "cannot transliterate" error):
#                  ===
#                       select 'gång: ' || current_timestamp from rdb$database                                                                                                                                                                                                                                                                          
#                       select 'g   
#                                ^^^
#                                 |
#                                 +--- three white-spaces here (after 'g')
#                  ===    
#                  No such effect on builds >= 2.1.3.18185.
#               
#                  Refactored 08-may-2017: replaced buggy "folder.replace()" with bulk of backslashes ("") with locals() usage.
#                  Checked again on Classic for: WI-V3.0.2.32708, WI-T4.0.0.633 
#                  (added expression to WHERE-block to filter out record from mon$statements with RDB$AUTH_MAPPING data).
#               
#                  02-MAR-2021:
#                  Changed code in order to remove dependency on PATH-list (CLI utilities must be invoked using context['..._path'])
#                  Full path+name of FB client library file is passed to generated Python code.
#                  Removed unneeded variables.
#               
#                  Checked on Windows: 4.0.0.2377 (SS/CS), 3.0.8.33420 (SS/CS), 2.5.9.27152 (SC)
#                  Checked on Linux:   4.0.0.2377, 3.0.8.33415.
#                
# tracker_id:   CORE-2531
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('SQL_TEXT_BLOB_ID .*', ''), ('[\t ]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import subprocess
#  import time
#  import codecs
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  engine = db_conn.engine_version
#  db_conn.close()
#  
#  svc = services.connect()
#  FB_HOME = os.path.normpath( svc.get_home_directory() ) # 'c:
#  irebird' --> 'c:
#  irebird' (i.e. remove trailing backslash if needed)
#  svc.close()
#  
#  FB_CLNT = '<UNKNOWN>'
#  if os.name == 'nt':
#      # For Windows we assume that client library is always in FB_HOME dir:
#      if engine < 3:
#          FB_CLNT=os.path.join(FB_HOME, 'bin', 'fbclient.dll')
#      else:
#          FB_CLNT=os.path.join(FB_HOME, 'fbclient.dll')
#  else:
#      # For Linux client library will be searched in 'lib' subdirectory of FB_HOME:
#      # con=fdb.connect( dsn='localhost:employee', fb_library_name='/var/tmp/fb40tmp/lib/libfbclient.so', ...)
#      FB_CLNT=os.path.join(FB_HOME, 'lib', 'libfbclient.so' )
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
#  #non_ascii_query="select 'gång' from rdb$database"
#  non_ascii_query=u"select 'gång' as non_ascii_literal from rdb$database"
#  
#  f_sql_txt='''
#      set count on;
#      set blob all;
#      set list on; 
#      select stored_sql_expr from non_ascii;
#      select
#          c.rdb$character_set_name as connection_charset
#         ,s.mon$sql_text as sql_text_blob_id
#      from mon$attachments a
#      left join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
#      left join mon$statements s on a.mon$attachment_id = s.mon$attachment_id
#      where
#          s.mon$attachment_id <> current_connection
#          and s.mon$sql_text containing 'non_ascii_literal'
#      ;
#  '''
#  
#  f_mon_sql = open( os.path.join(context['temp_directory'], 'tmp_2531_w1252.sql'), 'w' )
#  f_mon_sql.write(f_sql_txt)
#  flush_and_close( f_mon_sql )
#  
#  isql_path = context['isql_path']
#  isql_file = f_mon_sql.name
#  
#  ######################################################################
#  ###  t e m p o r a r y    P y t h o n    s c r i p t    s t ar t   ###
#  ######################################################################
#  f_python_txt='''# coding: latin-1
#  import os
#  import fdb
#  import subprocess
#  os.environ["ISC_USER"] = '%(user_name)s'
#  os.environ["ISC_PASSWORD"] = '%(user_password)s'
#  
#  att1 = fdb.connect(dsn = r'%(dsn)s', fb_library_name = r'%(FB_CLNT)s', charset = 'win1252')
#  att1.execute_immediate("recreate table non_ascii(stored_sql_expr varchar(255) character set win1252)")
#  att1.commit()
#  
#  txt = "%(non_ascii_query)s"
#  
#  cur1=att1.cursor()
#  cur1.execute( "insert into non_ascii(stored_sql_expr) values('%%s')"  %% txt.replace("'","''")  )
#  att1.commit()
#  
#  # The will cause SQL expression with non-ascii character
#  # appear in mon$statements.mon$sql_text column.
#  # NOTE: charset of current connection is >>> win1252 <<<
#  cur1.prep(txt)
#  
#  subprocess.call([ r'%(isql_path)s', r'%(dsn)s', '-ch', 'utf8', '-i', r'%(isql_file)s' ])
#  
#  cur1.close()
#  att1.commit()
#  att1.close()
#  ''' % dict(globals(), **locals())
#  ##############   temporary Python script finish   ###################
#  
#  
#  #####################################################################
#  ### Create temporary Python script with code page = Windows-1252, ###
#  ### so |select 'gång' from rdb$database| will be written there in ###
#  ### single-byte encoding rather than in utf8.                     ### 
#  ####################################################################
#  f_python_run=codecs.open( os.path.join(context['temp_directory'],'tmp_2531_w1252.py'), encoding='cp1252', mode='w')
#  f_python_run.write(f_python_txt)
#  
#  flush_and_close( f_python_run )
#  time.sleep(1)
#  
#  runProgram( sys.executable, [f_python_run.name] )
#  
#  # 02.03.2021 DO NOT! subprocess.call( [sys.executable, f_python_run.name] ) -- for unknown reason this will NOT issu anything to STDOUT!
#  
#  time.sleep(1)
#  
#  # 02.03.2021: do NOT pass to cleanup() files!
#  # It will fail with 'uknown type' for executed script ('f_python_run')
#  # because it will consider its type as 'instance' rather than common 'file'!
#  # We have to pass only NAMES list of used files here:
#  cleanup( [i.name for i in (f_python_run,f_mon_sql)] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    STORED_SQL_EXPR                 select 'gång' as non_ascii_literal from rdb$database
    Records affected: 1
    CONNECTION_CHARSET              WIN1252
    select 'gång' as non_ascii_literal from rdb$database
    Records affected: 1
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


