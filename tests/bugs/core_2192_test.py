#coding:utf-8
#
# id:           bugs.core_2192
# title:        Extend maximum database page size to 32KB
# decription:   
#                  We create DB with page_size = 32784, then add two table int it, both with UTF8 fields.
#                  First table (test_non_coll) has field which is based on trivial text domain.
#                  Second table (test_collated) has two 'domained' fields and both underlying domains are
#                  based on two collations: case_insensitive and case_insensitive + accent_insensitive.
#                  NOTE: we use MAXIMAL POSSIBLE length of every text field.
#                  Then we add to both tables some text data in order to check then correctness of queries
#                  which use several kinds of search (namely: starting with, like and between).
#                  Then we make validation, backup, restore and run again DML query and validation.
#                  Also, we do extraction of metadata before backup and after restore.
#                  Finally, we:
#                  1) check that all error logs are empty;
#                  2) compare logs of DML, metadata extraction - they should be identical.
#                
#                  Checked on 4.0.0.172, intermediate build based on sources of 10-may-2015 10:44 - works fine.
#                
# tracker_id:   CORE-2192
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

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
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#  
#  #-------------------------------------------
#  
#  db_conn.close()
#  
#  tmpfdb1=os.path.join(context['temp_directory'],'tmp_2192_32k.fdb')
#  if os.path.isfile(tmpfdb1):
#      os.remove(tmpfdb1)
#  
#  tmpfbk1=os.path.join(context['temp_directory'],'tmp_2192_32k.fbk')
#  if os.path.isfile(tmpfbk1):
#      os.remove(tmpfbk1)
#  
#  
#  test_size = 32768 # -- Ran 1 tests in 4.504s
#  # test_size = 16384 # -- Ran 1 tests in 2.735s
#  
#  max_indx1 = test_size / 4 - 9
#  max_indx6 = max_indx1 / 6
#  max_indx8 = max_indx1 / 8
#  
#  
#  sql_ddl='''    set list on;
#      set bail on;
#      set echo on;
#      create database 'localhost:%(tmpfdb1)s' page_size %(test_size)s;
#      select mon$page_size as page_size from mon$database;
#      commit;
#      create sequence g;
#      commit;
#      create collation utf8_ci for utf8 from unicode case insensitive;
#      create collation utf8_ai_ci for utf8 from unicode accent insensitive case insensitive ;
#      commit;
#      create domain dm_non_coll as varchar( %(max_indx1)s );
#      create domain dm_collated_ci as varchar( %(max_indx6)s ) character set utf8 collate utf8_ci;
#      create domain dm_collated_ai_ci as varchar( %(max_indx6)s ) character set utf8 collate utf8_ai_ci;
#      commit;
#      recreate table test_non_coll( 
#          txt_non_coll dm_non_coll
#      );
#      recreate table test_collated( 
#          txt_ci dm_collated_ci
#         ,txt_ai_ci dm_collated_ai_ci
#      );
#      commit;
#      create index test_non_coll on test_non_coll(txt_non_coll);
#      create index test_coll_ci on test_collated(txt_ci);
#      create index test_coll_ai_ci on test_collated(txt_ai_ci);
#      commit;
#  ''' % locals()
#  
#  dml_test = '''    --show version;
#      delete from test_non_coll;
#      delete from test_collated;
#      commit;
#      set count on;
#      insert into test_non_coll(txt_non_coll)
#      select 
#          rpad('', %(max_indx1)s, 'QWERTY' || gen_id(g,1)  )
#      from 
#      -- rdb$types rows 10000
#      (select 1 i from rdb$types rows 200), (select 1 i from rdb$types rows 5)
#      rows 361
#      ;
#      commit;
#  
#      insert into test_collated(txt_ci, txt_ai_ci)
#      select 
#          rpad('', %(max_indx6)s, 'Ещё Съешь Этих Мягких Французских Булочек Да Выпей Же Чаю')
#         ,rpad('', %(max_indx6)s, 'Ещё Французских Булочек Этих Мягких Съешь Да Чаю Выпей Же')
#      from 
#      (select 1 i from rdb$types rows 250), (select 1 i from rdb$types rows 2)
#      ;
#  
#      commit;
#  
#      set count off;
#      set list on;
#      set plan on;
#  
#      select count(*)
#      from test_non_coll
#      where txt_non_coll starting with 'QWERTY'
#  
#      union all
#  
#      select count(*)
#      from test_collated
#      where txt_ci starting with 'еЩё'
#  
#      union all
#  
#      select count(*)
#      from test_collated
#      where txt_ai_ci starting with 'ёЩЕ'
#  
#      union all
#  
#      select count(*)
#      from test_collated
#      where txt_ci = lower(rpad('', %(max_indx6)s, 'Ещё Съешь Этих Мягких Французских Булочек Да Выпей Же Чаю'))
#  
#      union all 
#  
#      select count(*)
#      from test_collated
#      where txt_ai_ci = rpad('', %(max_indx6)s, 'Ещё Французских Булочек Этих Мягких Съешь Да Чаю Выпей Же')
#      ;
#  
#      select count(*)
#      from test_non_coll
#      where txt_non_coll like 'QWERTY%%'
#  
#      union all
#  
#      select count(*)
#      from test_collated
#      where txt_ci like 'еЩё%%'
#  
#      union all
#  
#      select count(*)
#      from test_collated
#      where txt_ai_ci like 'ёЩЕ%%'
#  
#      union all
#  
#      select count(*)
#      from test_collated
#      where txt_ci between 
#      rpad('', %(max_indx6)s, 'ещё Съешь ЭТИХ Мягких Французских Булочек Да Выпей Же Чаю')
#      and
#      rpad('', %(max_indx6)s, 'ЕЩЁ Съешь Этих МЯГКИХ фРанцузских Булочек Да Выпей Же Чаю')
#  
#      union all 
#  
#      select count(*)
#      from test_collated
#      where txt_ai_ci between
#      rpad('', %(max_indx6)s, 'ёще фРанцузских Булочек Этих Мягких Съешь Да Чаю Выпёй Же')
#      and
#      rpad('', %(max_indx6)s, 'ёщё Французских Булочёк Этих Мягких Съёшь Да Чаю Выпёй Жё')
#      ;
#  
#      set plan off;
#  ''' % locals()
#  
#  f_create_db_32k_sql = open( os.path.join(context['temp_directory'],'tmp_2192_ddl.sql'), 'w')
#  f_create_db_32k_sql.write(sql_ddl)
#  f_create_db_32k_sql.close()
#  
#  # 0. CREATE DATABASE 
#  ####################
#  
#  f_create_db_32k_log = open( os.path.join(context['temp_directory'],'tmp_2192_ddl.log'), 'w')
#  f_create_db_32k_err = open( os.path.join(context['temp_directory'],'tmp_2192_ddl.err'), 'w')
#  subprocess.call( [ context['isql_path'], "-q", "-i", f_create_db_32k_sql.name, "-ch", "utf8" ]
#                   ,stdout = f_create_db_32k_log
#                   ,stderr = f_create_db_32k_err
#                 )
#  f_create_db_32k_log.close()
#  f_create_db_32k_err.close()
#  
#  # CHANGE FW to OFF
#  ##################
#  f_change_fw = open(os.devnull, 'w')
#  subprocess.call( [ context['fbsvcmgr_path'], "localhost:service_mgr", "action_properties", "dbname", tmpfdb1, "prp_write_mode", "prp_wm_async" ], stdout = f_change_fw,stderr = subprocess.STDOUT )
#  f_change_fw.close()
#  
#  # 1. FIRST RUN DML_TEST
#  #######################
#  
#  f_run_dml_sql = open( os.path.join(context['temp_directory'],'tmp_2192_dml.sql'), 'w')
#  f_run_dml_sql.write(dml_test)
#  f_run_dml_sql.close()
#  
#  f_run_dml_log_1 = open( os.path.join(context['temp_directory'],'tmp_2192_dml_1.log'), 'w')
#  subprocess.call( [ context['isql_path'], 'localhost:'+tmpfdb1, "-i", f_run_dml_sql.name, "-ch", "utf8" ]
#                   ,stdout = f_run_dml_log_1
#                   ,stderr = subprocess.STDOUT
#                 )
#  f_run_dml_log_1.close()
#  
#  # 2. EXTRACT METADATA-1
#  #######################
#  
#  f_extract_meta1_sql = open( os.path.join(context['temp_directory'],'tmp_2192_meta1.log'), 'w')
#  subprocess.call( [ context['isql_path'], 'localhost:'+tmpfdb1, "-x" ]
#                   ,stdout = f_extract_meta1_sql
#                   ,stderr = subprocess.STDOUT
#                 )
#  f_extract_meta1_sql.close()
#  
#  # 3. VALIDATE DATABASE-1
#  ########################
#  f_validate_log_1=open( os.path.join(context['temp_directory'],'tmp_2192_validate1.log'), "w")
#  f_validate_err_1=open( os.path.join(context['temp_directory'],'tmp_2192_validate1.err'), "w")
#  
#  subprocess.call( [ context['fbsvcmgr_path'],"localhost:service_mgr","action_validate","dbname", tmpfdb1 ],stdout=f_validate_log_1,stderr=f_validate_err_1 )
#  
#  f_validate_log_1.close()
#  f_validate_err_1.close()
#  
#  
#  # 4. TRY TO BACKUP AND RESTORE
#  ##############################
#  
#  f_backup_log=open( os.path.join(context['temp_directory'],'tmp_2192_backup.log'), "w")
#  f_backup_err=open( os.path.join(context['temp_directory'],'tmp_2192_backup.err'), "w")
#  
#  subprocess.call( [ context['fbsvcmgr_path'],"localhost:service_mgr","action_backup", "verbose","dbname", tmpfdb1, "bkp_file", tmpfbk1],stdout=f_backup_log,stderr=f_backup_err)
#  
#  f_backup_log.close()
#  f_backup_err.close()
#  
#  f_restore_log=open( os.path.join(context['temp_directory'],'tmp_2192_restore.log'), "w")
#  f_restore_err=open( os.path.join(context['temp_directory'],'tmp_2192_restore.err'), "w")
#  subprocess.call( [ context['fbsvcmgr_path'],"localhost:service_mgr",
#                     "action_restore", "res_replace", "verbose",
#                     "bkp_file", tmpfbk1, 
#                     "dbname", tmpfdb1 
#                   ]
#                   ,stdout=f_restore_log
#                   ,stderr=f_restore_err
#                 )
#  f_restore_log.close()                   
#  f_restore_err.close()                   
#  
#  # 5. EXTRACT METADATA-2
#  #######################
#  
#  f_extract_meta2_sql = open( os.path.join(context['temp_directory'],'tmp_2192_meta2.log'), 'w')
#  subprocess.call( [ context['isql_path'], 'localhost:'+tmpfdb1, "-x"],stdout = f_extract_meta2_sql,stderr = subprocess.STDOUT)
#  f_extract_meta2_sql.close()
#  
#  # 6. AGAIN RUN DML_TEST
#  #######################
#  
#  f_run_dml_log_2 = open( os.path.join(context['temp_directory'],'tmp_2192_dml_2.log'), 'w')
#  subprocess.call( [ context['isql_path'], 'localhost:'+tmpfdb1, "-i", f_run_dml_sql.name, "-ch", "utf8" ],stdout = f_run_dml_log_2,stderr = subprocess.STDOUT )
#  f_run_dml_log_2.close()
#  
#  # 7. VALIDATE DATABASE-2
#  ########################
#  f_validate_log_2=open( os.path.join(context['temp_directory'],'tmp_2192_validate2.log'), "w")
#  f_validate_err_2=open( os.path.join(context['temp_directory'],'tmp_2192_validate2.err'), "w")
#  
#  subprocess.call( [ context['fbsvcmgr_path'],"localhost:service_mgr","action_validate","dbname", tmpfdb1],stdout=f_validate_log_2,stderr=f_validate_err_2)
#  
#  f_validate_log_2.close()
#  f_validate_err_2.close()
#  
#  
#  # 7. CHECKS
#  ###########
#  # 1) STDERR for: create DB, backup, restore, validation-1 and validation-2 - they all must be EMPTY.
#  f_list=[]
#  f_list.append(f_create_db_32k_err)
#  f_list.append(f_validate_err_1)
#  f_list.append(f_backup_err)
#  f_list.append(f_restore_err)
#  f_list.append(f_validate_err_2)
#  
#  for i in range(len(f_list)):
#     f_name=f_list[i].name
#     if os.path.getsize(f_name) > 0:
#         with open( f_name,'r') as f:
#             for line in f:
#                 print("Unexpected STDERR, file "+f_name+": "+line)
#  
#  # 2) diff between dml_1.log and dml_2.log should be EMPTY.
#  # 3) diff between meta1.log and meta2.log should be EMPTY.
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_2192_diff.txt'), 'w')
#  f_old=[]
#  f_new=[]
#  
#  f_old.append(f_extract_meta1_sql) # DDL: what we have BEFORE database backup
#  f_old.append(f_run_dml_log_1)     # DML: result of querying tables before DB backup
#  f_new.append(f_extract_meta2_sql) # DDL: what we have AFTER database restore
#  f_new.append(f_run_dml_log_2)     # DML: result of querying tables AFTER database restore
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
#          print( 'Unexpected diff: '.join(line.split()).upper() )
#  
#  #####################################################################
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  
#  f_list= (
#      f_create_db_32k_sql
#      ,f_create_db_32k_log
#      ,f_create_db_32k_err
#      ,f_validate_log_1
#      ,f_validate_err_1
#      ,f_validate_log_2
#      ,f_validate_err_2
#      ,f_backup_log
#      ,f_backup_err
#      ,f_restore_log
#      ,f_restore_err
#      ,f_extract_meta1_sql
#      ,f_extract_meta2_sql
#      ,f_run_dml_sql
#      ,f_run_dml_log_1
#      ,f_run_dml_log_2
#      ,f_diff_txt
#  )
#  cleanup( [i.name for i in f_list] )
#  
#  os.remove(tmpfdb1) 
#  os.remove(tmpfbk1)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


