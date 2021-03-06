#coding:utf-8
#
# id:           bugs.core_4123
# title:        Firebird crash when executing an stored procedure called by a trigger that converts string to upper
# decription:   
#                   Confirmed problem on 2.5.2.26540 when trying convert iso8859_1 `y` with diersis sign to upper:
#                       Statement failed, SQLSTATE = 22001
#                       arithmetic exception, numeric overflow, or string truncation
#                       -string right truncation
#                   Checked on 2.5.326780 -- all OK.
#               
#                   02-mar-2021. Re-implemented in order to have ability to run this test on Linux.
#                   Test encodes to UTF8 all needed statements (SET NAMES; CONNECT; DDL and DML) and stores this text in .sql file.
#                   NOTE: 'SET NAMES' contain character set that must be used for reproducing problem (ISO8859_1 in this test).
#                   Then ISQL is launched in separate (child) process which performs all necessary actions (using required charset).
#                   Result will be redirected to log(s) which will be opened further via codecs.open(...encoding='iso-8859-1').
#                   Finally, its content will be converted to UTF8 for showing in expected_stdout.
#               
#                   Checked on:
#                           * Windows: 4.0.0.2377, 3.0.8.33420, 2.5.9.27152
#                           * Linux:   4.0.0.2377, 3.0.8.33415
#                 
# tracker_id:   CORE-4123
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import codecs
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
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  # Code to be executed further in separate ISQL process:
#  #############################
#  sql_txt='''    set bail on;
#      set names iso8859_1;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#  
#      set list on;
#      with recursive
#      d as (
#          select s, char_length(s) n
#          from (
#              -- http://www.ic.unicamp.br/~stolfi/EXPORT/www/ISO-8859-1-Encoding.html
#              -- ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ
#              select 'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ' as s
#              from rdb$database
#          )
#      )
#      ,r as(select 1 as i from rdb$database union all select r.i+1 from r where r.i<128)
#      ,c as(
#          select
#              substring(d.s from r.i for 1) as char_as_is
#              ,upper( substring(d.s from r.i for 1) ) char_upper
#              ,lower( substring(d.s from r.i for 1) ) char_lower
#          from d, r
#          where r.i <= d.n
#      )
#      select c.char_as_is, char_upper, char_lower, iif(char_upper = char_lower, '1',' ') is_upper_equ_lower
#      from c
#      order by 1
#      ;
#  ''' % dict(globals(), **locals())
#  
#  f_run_sql = open( os.path.join(context['temp_directory'], 'tmp_4123_iso8859_1.sql'), 'w' )
#  f_run_sql.write( sql_txt.decode('utf8').encode('iso-8859-1') )
#  flush_and_close( f_run_sql )
#  
#  # result: file tmp_4123_iso8859_1.sql is encoded in iso8859_1
#  
#  f_run_log = open( os.path.splitext(f_run_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_run_sql.name ],
#                   stdout = f_run_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_run_log ) # result: output will be encoded in iso8859_1
#  
#  with codecs.open(f_run_log.name, 'r', encoding='iso-8859-1' ) as f:
#      result_in_iso8859_1 = f.readlines()
#  
#  for i in result_in_iso8859_1:
#      print( i.encode('utf8') )
#  
#  # cleanup:
#  ###########
#  cleanup( (f_run_sql, f_run_log) )
#  
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CHAR_AS_IS                      À
    CHAR_UPPER                      À
    CHAR_LOWER                      à
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Á
    CHAR_UPPER                      Á
    CHAR_LOWER                      á
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Â
    CHAR_UPPER                      Â
    CHAR_LOWER                      â
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ã
    CHAR_UPPER                      Ã
    CHAR_LOWER                      ã
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ä
    CHAR_UPPER                      Ä
    CHAR_LOWER                      ä
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Å
    CHAR_UPPER                      Å
    CHAR_LOWER                      å
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Æ
    CHAR_UPPER                      Æ
    CHAR_LOWER                      æ
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ç
    CHAR_UPPER                      Ç
    CHAR_LOWER                      ç
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      È
    CHAR_UPPER                      È
    CHAR_LOWER                      è
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      É
    CHAR_UPPER                      É
    CHAR_LOWER                      é
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ê
    CHAR_UPPER                      Ê
    CHAR_LOWER                      ê
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ë
    CHAR_UPPER                      Ë
    CHAR_LOWER                      ë
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ì
    CHAR_UPPER                      Ì
    CHAR_LOWER                      ì
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Í
    CHAR_UPPER                      Í
    CHAR_LOWER                      í
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Î
    CHAR_UPPER                      Î
    CHAR_LOWER                      î
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ï
    CHAR_UPPER                      Ï
    CHAR_LOWER                      ï
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ð
    CHAR_UPPER                      Ð
    CHAR_LOWER                      ð
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ñ
    CHAR_UPPER                      Ñ
    CHAR_LOWER                      ñ
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ò
    CHAR_UPPER                      Ò
    CHAR_LOWER                      ò
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ó
    CHAR_UPPER                      Ó
    CHAR_LOWER                      ó
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ô
    CHAR_UPPER                      Ô
    CHAR_LOWER                      ô
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Õ
    CHAR_UPPER                      Õ
    CHAR_LOWER                      õ
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ö
    CHAR_UPPER                      Ö
    CHAR_LOWER                      ö
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ×
    CHAR_UPPER                      ×
    CHAR_LOWER                      ×
    IS_UPPER_EQU_LOWER              1

    CHAR_AS_IS                      Ø
    CHAR_UPPER                      Ø
    CHAR_LOWER                      ø
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ù
    CHAR_UPPER                      Ù
    CHAR_LOWER                      ù
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ú
    CHAR_UPPER                      Ú
    CHAR_LOWER                      ú
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Û
    CHAR_UPPER                      Û
    CHAR_LOWER                      û
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ü
    CHAR_UPPER                      Ü
    CHAR_LOWER                      ü
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Ý
    CHAR_UPPER                      Ý
    CHAR_LOWER                      ý
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      Þ
    CHAR_UPPER                      Þ
    CHAR_LOWER                      þ
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ß
    CHAR_UPPER                      ß
    CHAR_LOWER                      ß
    IS_UPPER_EQU_LOWER              1

    CHAR_AS_IS                      à
    CHAR_UPPER                      À
    CHAR_LOWER                      à
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      á
    CHAR_UPPER                      Á
    CHAR_LOWER                      á
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      â
    CHAR_UPPER                      Â
    CHAR_LOWER                      â
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ã
    CHAR_UPPER                      Ã
    CHAR_LOWER                      ã
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ä
    CHAR_UPPER                      Ä
    CHAR_LOWER                      ä
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      å
    CHAR_UPPER                      Å
    CHAR_LOWER                      å
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      æ
    CHAR_UPPER                      Æ
    CHAR_LOWER                      æ
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ç
    CHAR_UPPER                      Ç
    CHAR_LOWER                      ç
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      è
    CHAR_UPPER                      È
    CHAR_LOWER                      è
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      é
    CHAR_UPPER                      É
    CHAR_LOWER                      é
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ê
    CHAR_UPPER                      Ê
    CHAR_LOWER                      ê
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ë
    CHAR_UPPER                      Ë
    CHAR_LOWER                      ë
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ì
    CHAR_UPPER                      Ì
    CHAR_LOWER                      ì
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      í
    CHAR_UPPER                      Í
    CHAR_LOWER                      í
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      î
    CHAR_UPPER                      Î
    CHAR_LOWER                      î
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ï
    CHAR_UPPER                      Ï
    CHAR_LOWER                      ï
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ð
    CHAR_UPPER                      Ð
    CHAR_LOWER                      ð
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ñ
    CHAR_UPPER                      Ñ
    CHAR_LOWER                      ñ
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ò
    CHAR_UPPER                      Ò
    CHAR_LOWER                      ò
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ó
    CHAR_UPPER                      Ó
    CHAR_LOWER                      ó
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ô
    CHAR_UPPER                      Ô
    CHAR_LOWER                      ô
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      õ
    CHAR_UPPER                      Õ
    CHAR_LOWER                      õ
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ö
    CHAR_UPPER                      Ö
    CHAR_LOWER                      ö
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ÷
    CHAR_UPPER                      ÷
    CHAR_LOWER                      ÷
    IS_UPPER_EQU_LOWER              1

    CHAR_AS_IS                      ø
    CHAR_UPPER                      Ø
    CHAR_LOWER                      ø
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ù
    CHAR_UPPER                      Ù
    CHAR_LOWER                      ù
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ú
    CHAR_UPPER                      Ú
    CHAR_LOWER                      ú
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      û
    CHAR_UPPER                      Û
    CHAR_LOWER                      û
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ü
    CHAR_UPPER                      Ü
    CHAR_LOWER                      ü
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ý
    CHAR_UPPER                      Ý
    CHAR_LOWER                      ý
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      þ
    CHAR_UPPER                      Þ
    CHAR_LOWER                      þ
    IS_UPPER_EQU_LOWER

    CHAR_AS_IS                      ÿ
    CHAR_UPPER                      ÿ
    CHAR_LOWER                      ÿ
    IS_UPPER_EQU_LOWER              1
  """

@pytest.mark.version('>=2.5.3')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


