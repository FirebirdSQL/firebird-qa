#coding:utf-8
#
# id:           bugs.core_2408
# title:        isql -ex puts default values of sp parameters before the NOT NULL and COLLATE flags
# decription:   
#                  Quote from ticket: "make a procedure with NOT NULL and/or COLLATE flags *and* a default value on any parameter".
#                  Test enchances this by checking not only procedure but also function and package.
#                  Also, check is performed for table (I've encountered the same for TABLES definition in some old databases).
#               
#                  Algorithm is similar to test for core-5089: we create several DB objects which do have properties from ticket.
#                  Then we extract metadata and save it into file as 'initial' text.
#                  After this we drop all objects and make attempt to APPLY just extracted metadata script. It should perform without errors.
#                  Finally, we extract metadata again and do COMPARISON of their current content and those which are stored 'initial' file.
#               
#                  Checked on:  WI-V3.0.0.32328 (SS/CS/SC).
#                
# tracker_id:   CORE-2408
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set bail on;
    set autoddl off;
    commit;

    create collation nums_coll for utf8 from unicode case insensitive 'NUMERIC-SORT=1';
    create collation name_coll for utf8 from unicode no pad case insensitive accent insensitive;

    create domain dm_test varchar(20) character set utf8 default 'foo' not null collate nums_coll;

    create table test(
        s1 varchar(20) character set utf8 default 'foo' not null collate nums_coll
       ,s2 dm_test
       ,s3 dm_test default 'bar'
       ,s4 dm_test default 'rio' collate name_coll
    );

    set term ^;
    create or alter procedure sp_test(
        p1 varchar(20) character set utf8 not null collate nums_coll default 'foo'
       ,p2 dm_test default 'qwe'
       ,p3 dm_test default 'bar'
       ,p4 dm_test collate name_coll default 'rio'
    ) returns (
        o1 varchar(80)
       ,o2 dm_test collate name_coll
    )
    as
    begin
      o1 = lower(p1 || p2 || p3);
      o2 = upper(p4);
      suspend;
    end
    ^
    
    create or alter function fn_test(
        p1 varchar(20) character set utf8 not null collate nums_coll default 'foo'
       ,p2 dm_test default 'qwe'
       ,p3 dm_test default 'bar'
       ,p4 dm_test collate name_coll default 'rio'
    ) returns dm_test collate name_coll
    as
    begin
      return lower(left(p1,5) || left(p2,5) || left(p3,5) || left(p4,5));
    end
    ^

    recreate package pg_test as
    begin
        procedure pg_proc(
            p1 varchar(20) character set utf8 not null collate nums_coll default 'foo'
           ,p2 dm_test default 'qwe'
           ,p3 dm_test default 'bar'
           ,p4 dm_test collate name_coll default 'rio'
        ) returns (
            o1 varchar(80)
           ,o2 dm_test collate name_coll
        );
        function pg_func(
            p1 varchar(20) character set utf8 not null collate nums_coll default 'foo'
           ,p2 dm_test default 'qwe'
           ,p3 dm_test default 'bar'
           ,p4 dm_test collate name_coll default 'rio'
        ) returns dm_test collate name_coll;
    end
    ^

    create package body pg_test as
    begin
        procedure pg_proc(
            p1 varchar(20) character set utf8 not null collate nums_coll
           ,p2 dm_test
           ,p3 dm_test
           ,p4 dm_test collate name_coll
        ) returns (
            o1 varchar(80)
           ,o2 dm_test collate name_coll
        ) as
        begin
            o1 = lower(p1 || p2 || p3);
            o2 = upper(p4);
            suspend;
        end

        function pg_func(
            p1 varchar(20) character set utf8 not null collate nums_coll
           ,p2 dm_test
           ,p3 dm_test
           ,p4 dm_test collate name_coll
        ) returns dm_test collate name_coll as
        begin
            return lower(left(p1,5) || left(p2,5) || left(p3,5) || left(p4,5));
        end
    end
    ^
    set term ;^
    commit;
  """

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import subprocess
#  import time
#  import difflib
#  
#  #-----------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      os.fsync(file_handle.fileno())
#  
#      file_handle.close()
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
#  db_file=db_conn.database_name
#  db_conn.close()
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  f_extract_initial_meta_sql = open( os.path.join(context['temp_directory'],'tmp_meta_2408_init.sql'), 'w')
#  subprocess.call( [ context['isql_path'], dsn, "-x", "-ch", "utf8" ],
#                   stdout = f_extract_initial_meta_sql,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_extract_initial_meta_sql )
#  
#  ddl_clear_all='''
#      drop package pg_test;
#      drop function fn_test;
#      drop procedure sp_test;
#      drop table test;
#      drop domain dm_test;
#      drop collation name_coll;
#      drop collation nums_coll;
#      commit;
#  '''
#  
#  f_meta_drop_all_sql = open( os.path.join(context['temp_directory'],'tmp_meta_2408_drop_all.sql'), 'w')
#  f_meta_drop_all_sql.write(ddl_clear_all)
#  flush_and_close( f_meta_drop_all_sql )
#  
#  f_meta_drop_all_log = open( os.path.join(context['temp_directory'],'tmp_meta_2408_drop_all.log'), 'w')
#  subprocess.call( [ context['isql_path'], dsn, "-i", f_meta_drop_all_sql.name, "-ch", "utf8" ],
#                   stdout = f_meta_drop_all_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_meta_drop_all_log )
#  
#  
#  f_apply_extracted_meta_log = open( os.path.join(context['temp_directory'],'tmp_meta_2408_apply.log'), 'w')
#  subprocess.call( [ context['isql_path'], dsn, "-i", f_extract_initial_meta_sql.name, "-ch", "utf8" ],
#                   stdout = f_apply_extracted_meta_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_apply_extracted_meta_log )
#  
#  f_extract_current_meta_sql = open( os.path.join(context['temp_directory'],'tmp_meta_2408_last.sql'), 'w')
#  subprocess.call( [ context['isql_path'], dsn, "-x", "-ch", "utf8"],
#                   stdout = f_extract_current_meta_sql,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_extract_current_meta_sql )
#  
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_2408_meta_diff.txt'), 'w')
#  
#  f_old=[]
#  f_new=[]
#  
#  f_old.append(f_extract_initial_meta_sql) # tmp_meta_2408_init.sql -- extracted metadata just after 'init_script' was done
#  f_new.append(f_extract_current_meta_sql) # tmp_meta_2408_last.sql -- extracted metadata after drop all object and applying 'tmp_meta_2408_init.sql'
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
#  flush_and_close( f_diff_txt )
#  
#  
#  # Should be EMPTY:
#  ##################
#  with open( f_meta_drop_all_log.name, 'r') as f:
#      for line in f:
#          print( 'Error log of dropping existing objects: ' + f.line() )
#  
#  # Should be EMPTY:
#  ##################
#  with open( f_apply_extracted_meta_log.name, 'r') as f:
#      for line in f:
#          print( 'Error log of applying extracted metadata: ' + f.line() )
#  
#  # Should be EMPTY:
#  ##################
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#              print( ' '.join(line.split()).upper() )
#  
#  ###############################
#  # Cleanup.
#  time.sleep(1)
#  cleanup( [ i.name for i in (f_extract_initial_meta_sql,f_extract_current_meta_sql,f_meta_drop_all_sql,f_meta_drop_all_log,f_apply_extracted_meta_log,f_diff_txt) ] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


