#coding:utf-8
#
# id:           bugs.core_3489
# title:        Blob transliteration may not happen inside the union
# decription:
#               	02-mar-2021. Re-implemented in order to have ability to run this test on Linux.
#               	Test creates table and fills it with non-ascii characters in init_script, using charset = UTF8.
#               	Then it generates .sql script for running it in separae ISQL process.
#               	This script makes connection to test DB using charset = WIN1251 and perform needed DML.
#               	Result will be redirected to .log which will be opened via codecs.open(...encoding='cp1251').
#               	Its content will be converted to UTF8 for showing in expected_stdout.
#
#                   Confirmed bug on 2.5.0.26074: two lines with "raw" (not transliterated) data were displayed.
#                   Works OK on 2.5.1.26351: two readable lines will be issued.
#
# tracker_id:   CORE-3489
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 2.5.1
# resources: None

substitutions_1 = [('MSG_BLOB_ID.*', '')]

init_script_1 = """
	set term ^;
	create or alter procedure sp_test
	returns (
		msg_blob_id blob sub_type 1 segment size 80 character set unicode_fss)
	AS
	begin
		msg_blob_id= 'Это проверка на вывод строки "Йцукёнг"'; -- text in cyrillic
		suspend;
	end
	^
	set term ;^
	commit;
"""

db_1 = db_factory(charset='WIN1251', sql_dialect=3, init=init_script_1)

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
#
#  sql_txt='''    set names WIN1251;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#      set list on;
#      set blob all;
#  	set count on;
#  	set list on;
#
#  	select msg_blob_id
#  	from sp_test
#  	union
#  	select msg_blob_id
#  	from sp_test;
#  ''' % dict(globals(), **locals())
#
#  f_run_sql = open( os.path.join(context['temp_directory'], 'tmp_3489_win1251.sql'), 'w' )
#  f_run_sql.write( sql_txt.decode('utf8').encode('cp1251') )
#  flush_and_close( f_run_sql )
#  # result: file tmp_3489_win1251.sql is encoded in win1251
#
#  f_run_log = open( os.path.splitext(f_run_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_run_sql.name ],
#                   stdout = f_run_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_run_log ) # result: output will be encoded in win1251
#
#  with codecs.open(f_run_log.name, 'r', encoding='cp1251' ) as f:
#      result_in_cp1251 = f.readlines()
#
#  for i in result_in_cp1251:
#      print( i.encode('utf8') )
#
#  # cleanup:
#  ###########
#  cleanup( (f_run_sql, f_run_log) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Это проверка на вывод строки "Йцукёнг"
    Это проверка на вывод строки "Йцукёнг"
    Records affected: 2
"""

test_script_1 = temp_file('test_script.sql')

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action, test_script_1: Path):
    test_script_1.write_text("""
    set list on;
    set blob all;
    set count on;
    set list on;

    select msg_blob_id
    from sp_test
    union
    select msg_blob_id
    from sp_test;
    """, encoding='cp1251')
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=[], input_file=test_script_1, charset='WIN1251')
    assert act_1.clean_stdout == act_1.clean_expected_stdout


