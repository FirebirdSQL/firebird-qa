#coding:utf-8
#
# id:           bugs.core_1378
# title:        Domain names and charset issues
# decription:   
#                   05-mar-2021. Re-implemented in order to have ability to run this test on Linux.
#                   Test encodes to UTF8 all needed statements (SET NAMES; CONNECT; DDL and DML) and stores this text in .sql file.
#                   NOTE: 'SET NAMES' contain character set that must be used for reproducing problem (WIN1251 in this test).
#                   Then ISQL is launched in separate (child) process which performs all necessary actions (using required charset).
#                   Result will be redirected to log(s) which will be opened further via codecs.open(...encoding='cp1251').
#                   Finally, its content will be converted to UTF8 for showing in expected_stdout.
#                   Checked on:
#                   * Windows: 4.0.0.2377, 3.0.8.33423; 2.5.9.27152
#                   * Linux:   4.0.0.2379, 3.0.8.33415
#                 
# tracker_id:   
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         bugs.core_1378

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='WIN1251', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import codecs
#  import subprocess
#  import time
#  engine = db_conn.engine_version
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
#  sql_txt='''    set bail on;
#      set names win1251;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#  
#      create collation "вид прописи" for win1251 from pxw_cyrl pad space case insensitive accent insensitive;
#      commit;
#      create domain "значение числа" as int;
#      create domain "число прописью" as varchar(8191) character set win1251 collate "вид прописи";
#      commit;
#      create table test( id "значение числа", txt "число прописью");
#      commit;
#      set term ^;
#      create procedure sp_test ( i_number "значение числа") returns( o_text "число прописью") as
#      begin
#         suspend;
#      end
#      ^
#      set term ;^
#      commit;
#  
#      --set blob all;
#      --select rdb$procedure_source as rdb_source_blob_id from rdb$procedures where rdb$procedure_name = upper('sp_test');
#      set list on;
#  
#      select rdb$procedure_name from rdb$procedures where rdb$procedure_name = upper('sp_test');
#  
#      select
#          p.rdb$parameter_name
#          ,p.rdb$field_source
#          ,f.rdb$field_type
#          ,f.rdb$field_sub_type
#          ,f.rdb$field_length
#          ,f.rdb$character_length
#          ,f.rdb$character_set_id
#          ,f.rdb$collation_id
#          ,c.rdb$character_set_name
#          ,s.rdb$collation_name
#      from rdb$procedure_parameters p
#      left join rdb$fields f on p.rdb$field_source = f.rdb$field_name
#      left join rdb$character_sets c on f.rdb$character_set_id = c.rdb$character_set_id
#      left join rdb$collations s on
#          f.rdb$collation_id = s.rdb$collation_id
#          and c.rdb$character_set_id = s.rdb$character_set_id
#      where rdb$procedure_name = upper('sp_test')
#      ;
#  
#  
#  ''' % dict(globals(), **locals())
#  
#  f_run_sql = open( os.path.join(context['temp_directory'], 'tmp_1378_win1251.sql'), 'w' )
#  f_run_sql.write( sql_txt.decode('utf8').encode('cp1251') )
#  flush_and_close( f_run_sql )
#  
#  # result: file tmp_1378_win1251.sql is encoded in win1251
#  
#  f_run_log = open( os.path.splitext(f_run_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_run_sql.name ],
#                   stdout = f_run_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_run_log ) # result: output will be encoded in win1251
#  
#  with codecs.open(f_run_log.name, 'r', encoding='cp1251' ) as f:
#      result_in_win1251 = f.readlines()
#  
#  for i in result_in_win1251:
#      print( i.encode('utf8') )
#  
#  # cleanup:
#  ###########
#  cleanup( (f_run_sql, f_run_log) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$PROCEDURE_NAME              SP_TEST
    RDB$PARAMETER_NAME              I_NUMBER
    RDB$FIELD_SOURCE                значение числа
    RDB$FIELD_TYPE                  8
    RDB$FIELD_SUB_TYPE              0
    RDB$FIELD_LENGTH                4
    RDB$CHARACTER_LENGTH            <null>
    RDB$CHARACTER_SET_ID            <null>
    RDB$COLLATION_ID                <null>
    RDB$CHARACTER_SET_NAME          <null>
    RDB$COLLATION_NAME              <null>
    RDB$PARAMETER_NAME              O_TEXT
    RDB$FIELD_SOURCE                число прописью
    RDB$FIELD_TYPE                  37
    RDB$FIELD_SUB_TYPE              0
    RDB$FIELD_LENGTH                8191
    RDB$CHARACTER_LENGTH            8191
    RDB$CHARACTER_SET_ID            52
    RDB$COLLATION_ID                126
    RDB$CHARACTER_SET_NAME          WIN1251
    RDB$COLLATION_NAME              вид прописи
  """

@pytest.mark.version('>=2.5.9')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


