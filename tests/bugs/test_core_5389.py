#coding:utf-8
#
# id:           bugs.core_5389
# title:        Query cannot be executed if win1251 characters used in field aliases
# decription:   
#                   Test prepares file that will serve as input SQL script and will have CYRYLLIC names for field aliases.
#                   File has name = 'tmp_non_ascii_chk_5389.sql' and is encoded to windows-1251 codepage.
#                   Checked on 4.0.0.639.
#               	30.10.2019 checked on:
#               		4.0.0.1635 SS: 2.782s.
#               		4.0.0.1633 CS: 3.515s.	
#               	NB: old checked on: 4.0.0.639 - did pass without using codecs! Strange!
#                
# tracker_id:   CORE-5389
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('.*After line [0-9]+ in file .*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  
#  # 30.10.2019. This is needed in Python 2.7 for converting string in UTF8 to cp1251
#  import codecs
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
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  non_ascii_ddl='''
#      set list on;
#  	select
#  	   '' as "ФИО"
#  	  ,'' as "Д.рождения"
#  	  ,'' as "Город"
#  	  ,'' as "Расшифровка выступлений"
#  	from rdb$database;	
#  '''
#  
#  f_checksql=os.path.join(context['temp_directory'],'tmp_non_ascii_ddl_5389.sql')
#  with codecs.open( f_checksql, 'w', encoding='cp1251') as f:
#      f.write( non_ascii_ddl.decode('utf-8') )
#  
#  # Result: file 'tmp_non_ascii_chk_5389.sql' is encoded in cp1251 and contains SQL statements to be executed.
#  
#  ###########################################################################################################
#  ###  check-1:  attempt to apply DDL with non-ascii characters __WITHOUT__ charset specifying (for ISQL) ###
#  ###########################################################################################################
#  
#  f_apply_cset_none_log = open( os.path.join(context['temp_directory'],'tmp_5389_apply_cset_none.log'), 'w')
#  f_apply_cset_none_err = open( os.path.join(context['temp_directory'],'tmp_5389_apply_cset_none.err'), 'w')
#  
#  subprocess.call( ["isql", dsn, "-i", f_checksql ],
#                   stdout = f_apply_cset_none_log,
#                   stderr = f_apply_cset_none_err
#                 )
#  
#  f_apply_cset_none_log.close()
#  f_apply_cset_none_err.close()
#  
#  #############################################################################################################
#  ###  check-2:  attempt to apply DDL with non-ascii characters ___WITH___ specifying: ISQL ... -ch WIN1251 ###
#  #############################################################################################################
#  
#  f_apply_cset_1251_log = open( os.path.join(context['temp_directory'],'tmp_5389_apply_cset_1251.log'), 'w')
#  f_apply_cset_1251_err = open( os.path.join(context['temp_directory'],'tmp_5389_apply_cset_1251.err'), 'w')
#  
#  subprocess.call( ["isql", dsn, "-i", f_checksql, "-ch", "win1251" ],
#                   stdout = f_apply_cset_1251_log,
#                   stderr = f_apply_cset_1251_err
#                 )
#  
#  f_apply_cset_1251_log.close()
#  
#  # This file should NOT contain any errors:
#  f_apply_cset_1251_err.close()
#  
#  # do NOT remove this pause otherwise some of logs will not be enable for deletion and test will finish with 
#  # Exception raised while executing Python test script. exception: WindowsError: 32
#  time.sleep(1)
#  
#  
#  # CHECK RESULTS:
#  ################
#                 
#  # This stdout log should contain only ONE statement (create collation <non_ascii_name> ...),
#  # this DDL failed and caused ISQL to immediately terminate:
#  with open( f_apply_cset_none_log.name, 'r') as f:
#      for line in f:
#          out_txt='STDLOG WHEN CSET=NONE: ';
#          if line.strip():
#              print( out_txt+line.strip().decode("cp1251").encode('utf8') )
#  f.close()
#  
#  
#  with open( f_apply_cset_none_err.name, 'r') as f:
#      for line in f:
#          out_txt='STDERR WHEN CSET=NONE: ';
#          if line.strip():
#              print( out_txt+line.strip().decode("cp1251").encode('utf8') )
#          
#  f.close()
#  
#  
#  with open( f_apply_cset_1251_log.name, 'r') as f:
#      for line in f:
#          out_txt='STDLOG WHEN CSET=WIN1251: ';
#          if line.strip():
#              print( out_txt+line.strip().decode("cp1251").encode('utf8') )
#  f.close()
#  
#  with open( f_apply_cset_1251_err.name, 'r') as f:
#      for line in f:
#          out_txt='STDERR WHEN CSET=WIN1251: ';
#          if line.strip():
#              print( out_txt+line.strip().decode("cp1251").encode('utf8') )
#  f.close()
#  
#  
#  #####################################################################
#  # Cleanup:
#  
#  f_list = [ i.name for i in ( f_apply_cset_none_log, f_apply_cset_none_err, f_apply_cset_1251_log, f_apply_cset_1251_err ) ]
#  f_list += [ f_checksql, ]
#  cleanup( f_list )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    STDERR WHEN CSET=NONE: Statement failed, SQLSTATE = 22018
    STDERR WHEN CSET=NONE: arithmetic exception, numeric overflow, or string truncation
    STDERR WHEN CSET=NONE: -Cannot transliterate character between character sets
    STDLOG WHEN CSET=WIN1251: ФИО
    STDLOG WHEN CSET=WIN1251: Д.рождения
    STDLOG WHEN CSET=WIN1251: Город
    STDLOG WHEN CSET=WIN1251: Расшифровка выступлений  
  """

@pytest.mark.version('>=4.0')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_5389_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


