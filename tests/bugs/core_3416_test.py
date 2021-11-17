#coding:utf-8
#
# id:           bugs.core_3416
# title:        Inserting Käse into a CHARACTER SET ASCII column succeeds
# decription:
#               	02-mar-2021. Re-implemented in order to have ability to run this test on Linux.
#               	Test creates table and fills it with non-ascii characters in init_script, using charset = UTF8.
#               	Then it generates .sql script for running it in separae ISQL process.
#               	This script makes connection to test DB using charset = WIN1252 and perform needed DML.
#               	Result will be redirected to .log which will be opened via codecs.open(...encoding='cp1252').
#               	Its content will be converted to UTF8 for showing in expected_stdout.
#
#               	Checked on:
#               		* Windows: 4.0.0.2377, 3.0.8.33420, 2.5.9.27152
#               		* Linux:   4.0.0.2377, 3.0.8.33415
#
# tracker_id:   CORE-3416
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 2.5
# resources: None

substitutions_1 = [('After line .*', ''), ('[\t ]+', ' ')]

init_script_1 = """
    create table tascii(s_ascii varchar(10) character set ascii);
    create table tlatin(s_latin varchar(10) character set latin1);
    commit;
"""

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
#  sql_txt='''    set names WIN1252;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#      set list on;
#  	set count on;
#  	set echo on;
#  	insert into tascii values ('Käse');
#  	select s_ascii from tascii;
#
#  	insert into tlatin values ('Käse');
#  	select s_latin from tlatin;
#  ''' % dict(globals(), **locals())
#
#  f_run_sql = open( os.path.join(context['temp_directory'], 'tmp_3416_win1252.sql'), 'w' )
#  f_run_sql.write( sql_txt.decode('utf8').encode('cp1252') )
#  flush_and_close( f_run_sql )
#  # result: file tmp_3416_win1252.sql is encoded in win1252
#
#  f_run_log = open( os.path.splitext(f_run_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_run_sql.name ],
#                   stdout = f_run_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_run_log ) # result: output will be encoded in win1252
#
#  with codecs.open(f_run_log.name, 'r', encoding='cp1252' ) as f:
#      result_in_cp1252 = f.readlines()
#
#  for i in result_in_cp1252:
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
    insert into tascii values ('Käse');

    Records affected: 0

    select s_ascii from tascii;
    Records affected: 0

    insert into tlatin values ('Käse');
    Records affected: 1

    select s_latin from tlatin;
    S_LATIN                         Käse
    Records affected: 1
  """

expected_stderr_1 = """
Statement failed, SQLSTATE = 22018
arithmetic exception, numeric overflow, or string truncation
-Cannot transliterate character between character sets
After line 4 in file /tmp/pytest-of-pcisar/pytest-559/test_10/test_script.sql
"""

test_script_1 = temp_file('test_script.sql')

@pytest.mark.version('>=2.5')
def test_1(act_1: Action, test_script_1: Path):
    test_script_1.write_text("""
    set list on;
    set count on;
    set echo on;
    insert into tascii values ('Käse');
    select s_ascii from tascii;
    insert into tlatin values ('Käse');
    select s_latin from tlatin;
    """, encoding='cp1252')
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.isql(switches=[], input_file=test_script_1, charset='WIN1252')
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout



