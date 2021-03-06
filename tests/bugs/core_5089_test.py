#coding:utf-8
#
# id:           bugs.core_5089
# title:        Metadata extration (ISQL -X): "CREATE PROCEDURE/FUNCTION" statement contains reference to column of table(s) that not yet exists if this procedure had parameter of such type when it was created
# decription:   
#                  Test creates database with table 'TEST' and standalone and packaged procedures and functions which have parameters or variables 
#                  with referencing to the table 'TEST' column. Also, there are DB-level and DDL-level triggers with similar references.
#                  Then we extract metadata and save it into file as 'initial' text.
#                  After this we drop all objects and make attempt to APPLY just extracted metadata script. It should perform without errors.
#                  Finally, we extract metadata again and do COMPARISON of their current content and those which are stored 'initial' file.
#               
#                  Checked on:  WI-V3.0.0.32313 (SS/CS/SC). See also: test for CORE-2408.
#                
# tracker_id:   CORE-5089
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create domain dm_test int not null check ( value >=-1 );

    create table test(mode varchar(30), result dm_test);
    commit;

    set term ^;
    create procedure sp_test(
       i1 dm_test
      ,i2 type of dm_test
      ,i3 type of column test.result
    ) returns (
      o1 dm_test
      ,o2 type of dm_test
      ,o3 type of column test.result
    )
    as
      declare v1 dm_test = 3;
      declare v2 type of dm_test = 7;
      declare v3 type of column test.result = 9;
    begin
      o1 = v1 * i1;
      o2 = v2 * i2;
      o3 = v3 * i3;

      suspend;

    end
    ^

    create function fn_test(
       i1 dm_test
      ,i2 type of dm_test
      ,i3 type of column test.result
    ) returns type of column test.result
    as
      declare v1 dm_test = 11;
      declare v2 type of dm_test = 13;
      declare v3 type of column test.result = 17;
    begin
      return v1 * i1 + v2 * i2 + v3 * i3;
    end
    ^

    create package pg_test as
    begin
      procedure pg_proc(
         i1 dm_test
        ,i2 type of dm_test
        ,i3 type of column test.result
      ) returns (
        o1 dm_test
        ,o2 type of dm_test
        ,o3 type of column test.result
      );

      function pg_func(
         i1 dm_test
        ,i2 type of dm_test
        ,i3 type of column test.result
      ) returns type of column test.result;
    end
    ^

    create package body pg_test as
    begin
      procedure pg_proc(
         i1 dm_test
        ,i2 type of dm_test
        ,i3 type of column test.result
      ) returns (
        o1 dm_test
        ,o2 type of dm_test
        ,o3 type of column test.result
      ) as
        declare v1 dm_test = 19;
        declare v2 type of dm_test = 23;
        declare v3 type of column test.result = 29;
      begin

        o1 = v1 * i1;
        o2 = v2 * i2;
        o3 = v3 * i3;

        suspend;

      end

      function pg_func(
         i1 dm_test
        ,i2 type of dm_test
        ,i3 type of column test.result
      ) returns type of column test.result as
        declare v1 dm_test = 13;
        declare v2 type of dm_test = 17;
        declare v3 type of column test.result = 19;
      begin
        return v1 * i1 + v2 * i2 + v3 * i3;
      end

    end
    ^
    create or alter trigger trg_connect on connect as
        declare v1 dm_test = 19;
        declare v2 type of dm_test = 23;
        declare v3 type of column test.result = 29;
    begin
        /* 1st db-level trigger, on CONNECT event */
    end
    ^

    create or alter trigger trg_commit on transaction commit as
        declare v1 dm_test = 19;
        declare v2 type of dm_test = 23;
        declare v3 type of column test.result = 29;
    begin
        /* 2nd db-level trigger, on transaction COMMIT event */
    end
    ^

    create or alter trigger trg_ddl_before before any ddl statement
    as
        declare v1 dm_test = 19;
        declare v2 type of dm_test = 23;
        declare v3 type of column test.result = 29;
    begin
        /* DDL-level trigger before any ddl statement */
    end
    ^

    set term ^;
    commit;
  """

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  import difflib
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_file = db_conn.database_name
#  db_conn.close()
#  
#  #--------------------------------------------
#  
#  def flush_and_close(file_handle):
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
#  f_extract_initial_meta_sql = open( os.path.join(context['temp_directory'],'tmp_meta_5089_init.sql'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-x", "-ch", "utf8"],
#                   stdout = f_extract_initial_meta_sql,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_extract_initial_meta_sql )
#  
#  ddl_clear_all='''
#      drop trigger trg_ddl_before;
#      drop trigger trg_commit;
#      drop trigger trg_connect;
#      drop package pg_test;
#      drop function fn_test;
#      drop procedure sp_test;
#      drop table test;
#      drop domain dm_test;
#      commit;
#  '''
#  
#  f_meta_drop_all_sql = open( os.path.join(context['temp_directory'],'tmp_meta_5089_drop_all.sql'), 'w')
#  f_meta_drop_all_sql.write(ddl_clear_all)
#  flush_and_close( f_meta_drop_all_sql )
#  
#  f_meta_drop_all_log = open( os.path.join(context['temp_directory'],'tmp_meta_5089_drop_all.log'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-i", f_meta_drop_all_sql.name, "-ch", "utf8" ],
#                   stdout = f_meta_drop_all_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_meta_drop_all_log )
#  
#  
#  f_apply_extracted_meta_log = open( os.path.join(context['temp_directory'],'tmp_meta_5089_apply.log'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-i", f_extract_initial_meta_sql.name, "-ch", "utf8" ],
#                   stdout = f_apply_extracted_meta_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_apply_extracted_meta_log )
#  
#  f_extract_current_meta_sql = open( os.path.join(context['temp_directory'],'tmp_meta_5089_last.sql'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-x", "-ch", "utf8"],
#                   stdout = f_extract_current_meta_sql,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_extract_current_meta_sql )
#  
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_5089_meta_diff.txt'), 'w')
#  
#  f_old=[]
#  f_new=[]
#  
#  f_old.append(f_extract_initial_meta_sql) # tmp_meta_5089_init.sql -- extracted metadata just after 'init_script' was done
#  f_new.append(f_extract_current_meta_sql) # tmp_meta_5089_last.sql -- extracted metadata after drop all object and applying 'tmp_meta_5089_init.sql'
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
#  
#  # Should be EMPTY:
#  ##################
#  with open( f_apply_extracted_meta_log.name, 'r') as f:
#      for line in f:
#          print( 'Error log of applying extracted metadata: ' + f.line() )
#  
#  
#  # Should be EMPTY:
#  ##################
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#              print( ' '.join(line.split()).upper() )
#  
#  
#  
#  # CLEANUP.
#  ##########
#  time.sleep(1)
#  cleanup( (f_extract_initial_meta_sql,f_extract_current_meta_sql,f_meta_drop_all_sql,f_meta_drop_all_log,f_apply_extracted_meta_log,f_diff_txt) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


