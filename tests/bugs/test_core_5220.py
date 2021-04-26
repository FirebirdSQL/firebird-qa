#coding:utf-8
#
# id:           bugs.core_5220
# title:        ISQL -X: double quotes are missed for COLLATE <C> of CREATE DOMAIN statement when <C> is from any non-ascii charset
# decription:   
#                  We create in init_script two collations with non-ascii names and two varchar domains which use these collations.
#                  Then we extract metadata and save it to file as .sql script to be applied further.
#                  This script should contain CORRECT domains definition, i.e. collations should be enclosed in double quotes.
#                  We check correctness by removing from database all objects and applying this script: no errors should occur at that point.
#                  Then we extract metadata second time, store it to second .sql and COMPARE this file with result of first metadata extraction.
#                  These files should be equal, i.e. difference should be empty.
#                  
#                  Checked on WI-V3.0.0.32501, WI-T4.0.0.155.
#                
# tracker_id:   CORE-5220
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create collation "Циферки" for utf8 from unicode case insensitive 'NUMERIC-SORT=1';
    create collation "Испания" for iso8859_1 from es_es_ci_ai 'SPECIALS-FIRST=1';;
    commit;
    create domain "Артикулы" varchar(12) character set utf8 collate "Циферки";
    create domain "Комрады" varchar(40) character set iso8859_1 collate "Испания";
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  import difflib
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  f_extract_meta1_sql = open( os.path.join(context['temp_directory'],'tmp_5220_meta1.sql'), 'w')
#  subprocess.call( ["isql", dsn, "-x"],
#                   stdout = f_extract_meta1_sql,
#                   stderr = subprocess.STDOUT
#                 )
#  f_extract_meta1_sql.close()
#  
#  f_remove_meta_sql = open( os.path.join(context['temp_directory'],'tmp_5220_kill.sql'), 'w')
#  f_remove_meta_sql.write('drop domain "Комрады"; drop domain "Артикулы"; drop collation "Испания"; drop collation "Циферки"; commit; show domain; show collation;')
#  f_remove_meta_sql.close()
#  
#  f_remove_meta_log = open( os.path.join(context['temp_directory'],'tmp_5220_kill.log'), 'w')
#  subprocess.call( ["isql", dsn, "-ch", "utf8", "-i", f_remove_meta_sql.name],
#                   stdout = f_remove_meta_log,
#                   stderr = subprocess.STDOUT
#                 )
#  f_remove_meta_log.close()               
#                 
#  f_apply_meta_log = open( os.path.join(context['temp_directory'],'tmp_5220_apply.log'), 'w')
#  subprocess.call( ["isql", dsn, "-ch", "utf8", "-i", f_extract_meta1_sql.name],
#                   stdout = f_apply_meta_log,
#                   stderr = subprocess.STDOUT
#                 )
#  f_apply_meta_log.close()
#  
#  
#  f_extract_meta2_sql = open( os.path.join(context['temp_directory'],'tmp_5220_meta2.sql'), 'w')
#  subprocess.call( ["isql", dsn, "-x"],
#                   stdout = f_extract_meta2_sql,
#                   stderr = subprocess.STDOUT
#                 )
#  f_extract_meta2_sql.close()
#            
#  time.sleep(1)
#            
#  ###############
#  # CHECK RESULTS
#  ###############
#  
#  # 1. Log f_remove_meta_log (REMOVING metadata) should contain only phrases about absence of domains and collations
#  with open( f_remove_meta_log.name, 'r') as f:
#      for line in f:
#          if line.strip():
#              print('REMOVE METADATA LOG: '+line)
#  f.close()
#  
#  # 2. Log f_apply_meta_log (result of APPLYING extracted metadata, file: f_extract_meta1_sql) should be EMPTY 
#  #    (because collation names now should be enclosed in double quotes)
#  with open( f_apply_meta_log.name, 'r') as f:
#      for line in f:
#          if line.strip():
#              print('APPLY EXTRACTED METADATA LOG: '+line)
#  f.close()
#  
#  # 3. Log f_extract_meta2_sql should EXACTLY match to first extracted metadata log (f_extract_meta1_sql).
#  #    We compare these files using Python 'diff' package.
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_5220_meta_diff.txt'), 'w')
#  
#  f_old=[]
#  f_new=[]
#  
#  f_old.append(f_extract_meta1_sql) # tmp_5220_meta1.sql -- extracted metadata just after 'init_script' was done
#  f_new.append(f_extract_meta2_sql) # tmp_5220_meta2.sql -- extracted metadata after drop all object and applying 'f_extract_meta1_sql'
#  
#  for i in range(len(f_old)):
#      old_file=open(f_old[i].name,'r')
#      new_file=open(f_new[i].name,'r')
#      
#      f_diff_txt.write( ''.join( difflib.unified_diff( old_file.readlines(), new_file.readlines() ) ) )
#  
#      old_file.close()
#      new_file.close()
#  
#  f_diff_txt.close()
#  
#  # Should be EMPTY:
#  ##################
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#              print( 'METADATA DIFF:' + ' '.join(line.split()).upper() )
#  f.close()
#  
#  #####################################################################
#  # Cleanup:
#  
#  f_list=[]
#  f_list.append(f_extract_meta1_sql)
#  f_list.append(f_extract_meta2_sql)
#  f_list.append(f_apply_meta_log)
#  f_list.append(f_remove_meta_log)
#  f_list.append(f_remove_meta_sql)
#  f_list.append(f_diff_txt)
#  
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i].name):
#          os.remove(f_list[i].name)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    REMOVE METADATA LOG: There are no domains in this database
    REMOVE METADATA LOG: There are no user-defined collations in this database  
  """

@pytest.mark.version('>=3.0')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_5220_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


