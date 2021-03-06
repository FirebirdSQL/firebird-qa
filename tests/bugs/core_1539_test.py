#coding:utf-8
#
# id:           bugs.core_1539
# title:        select * from rdb$triggers where rdb$trigger_source like 'CHECK%'
# decription:   
#                   ::: NOTE :::
#                   In order to check correctness of following statements under ISQL itself (NOT under fbt_run), do following:
#                   1) open some text editor that supports charset = win1251 and set encoding for new document = WIN1251
#                     (e.g. in Notepad++ pull-down menu: "Encoding / Character sets / Cyrillic / Windows 1251")
#                   2) type text save to .sql
#                   3) open this .sql in FAR editor and ensure that letters are displayed as SINGLE-BYTE characters
#                   4) run isql -i <script_encoded_in_win1251.sql>
#                   In order to run this script under fbt_run:
#                   1) open Notepad++ new .fbt document and set Encoding = "UTF8 without BOM"
#                   2) copy-paste text from <script_encoded_in_win1251.sql>, ensure that letters remains readable
#                      (it should be pasted here in UTF8 encoding)
#                   3) add in `expected_stdout` section required output by copy-paste from result of isql -i <script_encoded_in_win1251.sql>
#                      (it should be pasted here in UTF8 encoding)
#                   4) save .fbt and ensure that it was saved in UTF8 encoding, otherwise exeption like
#                      "UnicodeDecodeError: 'utf8' codec can't decode byte 0xc3 in position 621: invalid continuation byte"
#                      will raise.
#               
#               
#                   02-mar-2021. Re-implemented in ordeer to have ability to run this test on Linux.
#                   We run 'init_script' using charset = utf8 but then run separate ISQL-process
#                   with request to establish connection using charset = WIN1251.
#                   Its output is redirected to separate files. File with results of errors (STDERR) must remain empty.
#                   If it contain anything, we use codecs.open(..., 'r', 'cp1251') + encode('utf8') to display its content.
#               
#                   Checked on:
#                   * Windows: 4.0.0.2377, 3.0.8.33420, 2.5.9.27152
#                   * Linux:   4.0.0.2377, 3.0.8.33415
#               
#                 
# tracker_id:   CORE-1539
# min_versions: ['2.1']
# versions:     2.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """
	-- ### ONCE AGAIN ###
	-- 1) for checking this under ISQL following must be encoded in WIN1251
	-- 2) for running under fbt_run utility following must be encoded in UTF8.
    recreate table test (
        bugtype         varchar(20),
        bugfrequency    varchar(20),
        decision        varchar(20),
        fixerkey        int,
        decisiondate date
    );
    
    alter table test
        add constraint test_bugtype check (bugtype in ('зрабіць', 'трэба зрабіць', 'недахоп', 'памылка', 'катастрофа'))
        ,add constraint test_bugfrequency check (bugfrequency in ('ніколі', 'зрэдку', 'часам', 'часта', 'заўсёды', 'не прыкладаецца'))
        ,add constraint test_decision check (decision in ('адкрыта', 'зроблена', 'састарэла', 'адхілена', 'часткова', 'выдалена'))
        ,add constraint test_fixerkey check ((decision = 'адкрыта' and fixerkey is null and decisiondate is null) or (decision <> 'адкрыта' and not fixerkey is null and not decisiondate is null))
    ;
    commit;
  """

db_1 = db_factory(charset='WIN1251', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import time
#  import codecs
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
#  sql_cmd='''
#      set names WIN1251;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#      set blob all;
#      set list on;
#      -- Ticket:
#      -- select * from rdb$triggers where rdb$trigger_source like 'CHECK%%' ==> "Cannot transliterate character between character sets."
#      -- select * from rdb$triggers where rdb$trigger_source starting 'CHECK' ==> works fine.
#      select rdb$trigger_name, rdb$trigger_source
#      from rdb$triggers 
#      where rdb$trigger_source like 'check%%'
#      order by cast(replace(rdb$trigger_name, 'CHECK_', '') as int);
#  	;
#  ''' % dict(globals(), **locals())
#  
#  f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_1539_run.sql'), 'w')
#  f_sql_chk.write(sql_cmd)
#  flush_and_close( f_sql_chk )
#  
#  f_sql_log = open( ''.join( (os.path.splitext(f_sql_chk.name)[0], '.log' ) ), 'w')
#  f_sql_err = open( ''.join( (os.path.splitext(f_sql_chk.name)[0], '.err' ) ), 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_sql_chk.name ], stdout = f_sql_log, stderr = f_sql_err)
#  flush_and_close( f_sql_log )
#  flush_and_close( f_sql_err )
#  
#  # If any error occurs --> open .err file and convert messages from there (encoded in win1251) to utf-8:
#  # 
#  with codecs.open(f_sql_err.name,'r', encoding='cp1251') as f:
#      for line in f:
#          if line:
#              print( 'Unexpected STDERR, line: %s' % line.encode('utf-8') )
#  
#  cleanup( (f_sql_chk, f_sql_log, f_sql_err) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


