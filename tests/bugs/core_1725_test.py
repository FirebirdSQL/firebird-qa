#coding:utf-8
#
# id:           bugs.core_1725
# title:        Unable to restore a database with inactive indices if any SP/trigger contains an explicit plan
# decription:   
#                   We create database and add a table with two indices there.
#                   Then we create several program objects that use these indices explicitly by specifying 'PLAN' clause:
#                   view, standalone procedure, standalone function, packaged procedure and function and DB-level trigger.
#                   We also create several units that do not use these index explicitly.
#                   Then we extract metadata from this DB ans saved in "initial" .sql, see 'f_meta_init' var.
#               
#                   After this, we do backup and restore (using PIPE mechanism in order to avoid creation of unneeded .fbk).
#                   Restored database is further renamed to initial name and we do on this DB:
#                   * full validation and
#                   * metadata extraction, see 'f_meta_rest' var.
#               
#                   Result of validation must be "0 errors and 0 warnings".
#                   Result of extracted metadata comparison must be empty (no difference). ALL program objects must be preserved.
#               
#                   Checked on:
#                       4.0.0.1881 SS: 6.238s.
#                       4.0.0.1391 SC: 12.503s.
#                       3.0.6.33283 SS: 3.859s.
#                       3.0.6.33276 SS: 4.002s.
#               
#                   ::: NB ::: This bug was fixed between 17-dec-2018 and 23-jan-2019.
#                   Builds 4.0.0.1346 and 3.0.5.33084 (both of 17.12.2018) still have bug: no program units will be in restored DB.
#                   Builds 4.0.0.1391 (23.01.2019) and 3.0.5.33097 (01.02.2019) work fine.
#                
# tracker_id:   CORE-1725
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import shutil
#  import difflib
#  import subprocess
#  from subprocess import Popen
#  from subprocess import PIPE
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  DB_PATH = os.sep.join( db_conn.database_name.split(os.sep)[:-1] )
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
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
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
#  def svc_get_fb_log( f_fb_log ):
#  
#    global subprocess
#    subprocess.call( [ context['fbsvcmgr_path'],
#                       "localhost:service_mgr",
#                       "action_get_fb_log"
#                     ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
#  
#  #--------------------------------------------
#  
#  tmp_initdb = os.path.join(context['temp_directory'],'tmp_1725_init.fdb')
#  tmp_restdb = os.path.join(context['temp_directory'],'tmp_1725_rest.fdb')
#  
#  cleanup( (tmp_initdb, tmp_restdb,) )
#  
#  sql_init='''
#      set bail on;
#  
#      create database 'localhost:%(tmp_initdb)s' user %(user_name)s password '%(user_password)s';
#   
#      create or alter procedure sp_init as begin end;
#      create or alter procedure sp_main as begin end;
#      create or alter procedure sp_worker as begin end;
#  
#      create or alter function fn_init returns int as begin end;
#      create or alter function fn_main returns int as begin end;
#      create or alter function fn_worker returns int as begin end;
#  
#  
#      create table test(id int primary key, x int, y int);
#      create index test_x on test(x);
#      create descending index test_y on test(y);
#      commit;
#   
#      insert into test(id, x, y) select row_number()over(), rand()*5, rand()*100 from rdb$types;
#      commit;
#   
#      create or alter view v_init as
#          select count(*) as cnt from test group by x
#          rows 1
#      ;
#   
#      create or alter view v_worker as
#          select count(*) as cnt
#          from test 
#          group by y
#          plan (TEST ORDER TEST_Y)
#          union all
#          select cnt from v_init
#      ;
#      commit;
#   
#   
#      set term ^;
#      execute block as
#      begin
#          rdb$set_context('USER_SESSION','INITIAL_DDL', '1');
#      end
#      ^
#  
#      create or alter procedure sp_init as
#          declare c int;
#      begin
#          select count(*) from test group by x
#          rows 1
#          into c
#          ;
#      end
#      ^
#   
#      create or alter procedure sp_main as
#      begin
#          execute procedure sp_worker;
#      end
#      ^
#   
#      create or alter procedure sp_worker as
#          declare c int;
#      begin
#          select sum(cnt)
#          from (
#              select count(*) as cnt 
#              from test group by x
#              plan (TEST ORDER TEST_X)
#              union all
#              select cnt from v_worker
#          )
#          into c
#          ;
#      end
#      ^
#      create or alter function fn_init returns int as
#      begin
#          return ( select count(*) from test );
#      end
#      ^
#      create or alter function fn_worker returns int as
#      begin
#          return (
#              select sum(cnt)
#              from (
#                  select count(*) as cnt 
#                  from test group by x
#                  plan (TEST ORDER TEST_X)
#                  union all
#                  select cnt from v_worker
#              )
#          );
#      end
#      ^
#      create or alter function fn_main returns int as
#      begin
#          return fn_worker();
#      end
#      ^
#  
#      create or alter package pg_test as
#      begin
#          function pg_fn_worker returns int;
#          procedure pg_sp_worker;
#      end
#      ^
#      recreate package body pg_test as
#      begin
#          function pg_fn_worker returns int as
#          begin
#              return (
#                  select sum(cnt)
#                  from (
#                      select count(*) as cnt 
#                      from test group by x
#                      plan (TEST ORDER TEST_X)
#                      union all
#                      select cnt from v_worker
#                  )
#              );
#          end
#  
#          procedure pg_sp_worker as
#              declare c int;
#          begin
#              select sum(cnt)
#              from (
#                  select count(*) as cnt 
#                  from test group by x
#                  plan (TEST ORDER TEST_X)
#                  union all
#                  select cnt from v_worker
#              )
#              into c
#              ;
#          end
#  
#      end
#      ^
#  
#      create or alter trigger trg_attach active on connect position 0 as
#          declare c int;
#      begin
#          if ( rdb$get_context('USER_SESSION','INITIAL_DDL') is null ) then
#          begin
#              select sum(cnt)
#              from (
#                  select count(*) as cnt 
#                  from test group by x
#                  plan (TEST ORDER TEST_X)
#                  union all
#                  select cnt from v_worker
#              )
#              into c;
#          end
#      end
#      ^
#      set term ;^
#      commit;
#  ''' % dict(globals(), **locals())
#  
#  f_init_sql=open( os.path.join(context['temp_directory'],'tmp_1725_init.sql'), 'w')
#  f_init_sql.write(sql_init)
#  f_init_sql.close()
#  
#  f_init_log=open( os.path.join(context['temp_directory'],'tmp_1725_init.log'), 'w', buffering = 0)
#  f_init_err=open( os.path.join(context['temp_directory'],'tmp_1725_init.err'), 'w', buffering = 0)
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_init_sql.name], stdout=f_init_log, stderr=f_init_err )
#  flush_and_close( f_init_log )
#  flush_and_close( f_init_err )
#  
#  #----------------------------------------------------------------------
#  
#  # Extract metadata from initial DB:
#  ##################
#  f_meta_init=open( os.path.join(context['temp_directory'],'tmp_1725_meta.init.sql'), 'w', buffering = 0)
#  subprocess.call( [ context['isql_path'], '-nod', '-x', 'localhost:'+tmp_initdb ], stdout=f_meta_init, stderr=subprocess.STDOUT )
#  flush_and_close( f_meta_init )
#  
#  #----------------------------------------------------------------------
#  
#  # backup  + restore _WITHOUT_ building indices:
#  ###################
#  # https://docs.python.org/2/library/subprocess.html#replacing-shell-pipeline
#  p_sender = subprocess.Popen( [ context['gbak_path'], '-b', 'localhost:'+tmp_initdb, 'stdout' ], stdout=PIPE)
#  p_getter = subprocess.Popen( [ context['gbak_path'], '-c', '-i', 'stdin',  tmp_restdb ], stdin = p_sender.stdout, stdout = PIPE )
#  p_sender.stdout.close()
#  p_getter_stdout, p_getter_stderr = p_getter.communicate()
#  
#  #----------------------------------------------------------------------
#  
#  # Get FB log before validation, run validation and get FB log after it:
#  ############
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_1725_fblog_before_validation.txt'), 'w')
#  svc_get_fb_log( f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  f_validate_log=open( os.path.join(context['temp_directory'],'tmp_1725_validate.log'), 'w', buffering = 0)
#  f_validate_err=open( os.path.join(context['temp_directory'],'tmp_1725_validate.err'), 'w', buffering = 0)
#  subprocess.call( [ context['gfix_path'], '-v', '-full', 'localhost:'+tmp_restdb ], stdout=f_validate_log, stderr=f_validate_err )
#  flush_and_close( f_validate_log )
#  flush_and_close( f_validate_err )
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_1725_fblog__after_validation.txt'), 'w')
#  svc_get_fb_log( f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  #----------------------------------------------------------------------
#  shutil.move(tmp_restdb, tmp_initdb)
#  #----------------------------------------------------------------------
#  
#  # Extract metadata from restored DB:
#  ##################
#  f_meta_rest=open( os.path.join(context['temp_directory'],'tmp_1725_meta.rest.sql'), 'w', buffering = 0)
#  subprocess.call( [ context['isql_path'], '-nod', '-x', 'localhost:'+tmp_initdb ], stdout=f_meta_rest, stderr=subprocess.STDOUT )
#  flush_and_close( f_meta_rest )
#  
#  #----------------------------------------------------------------------
#  
#  oldmeta=open(f_meta_init.name, 'r')
#  newmeta=open(f_meta_rest.name, 'r')
#  
#  diffmeta = ''.join(difflib.unified_diff(
#      oldmeta.readlines(), 
#      newmeta.readlines()
#    ))
#  oldmeta.close()
#  newmeta.close()
#  
#  f_meta_diff=open( os.path.join(context['temp_directory'],'tmp_1725_meta_diff.txt'), 'w', buffering = 0)
#  f_meta_diff.write(diffmeta)
#  flush_and_close( f_meta_diff )
#  
#  #----------------------------------------------------------------------
#  
#  # Compare firebird.log versions BEFORE and AFTER this test:
#  ######################
#  
#  oldfb=open(f_fblog_before.name, 'r')
#  newfb=open(f_fblog_after.name, 'r')
#  
#  difftext = ''.join(difflib.unified_diff(
#      oldfb.readlines(), 
#      newfb.readlines()
#    ))
#  oldfb.close()
#  newfb.close()
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_5719_valid_diff.txt'), 'w', buffering = 0)
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  #-----------------------------------------------------------------------
#  
#  # CHECKS:
#  #########
#  
#  # Logs of initial .sql must be empty.
#  # Result of diff in extracted metadata .sql must be empty.
#  # Output of 'gfix -v -full' must be empty.
#  for g in (f_init_log, f_init_err, f_meta_diff, f_validate_log, f_validate_err):
#      with open(g.name, 'r') as f:
#          for line in f:
#              if line.split():
#                  print('UNEXPECTED OUTPUT in ' + os.path.split(g.name)[-1] + ': ' + line )
#  
#  # Result of diff in firebird.log before and after validation must contain text with ZERO warninngs and ZERO errors:
#  # +	Validation finished: 0 errors, 0 warnings, 0 fixed
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+') and 'Validation' in line:
#              print( line )
#  
#  # Cleanup:
#  ##########
#  
#  # do NOT remove this pause otherwise some of logs will not be enable for deletion and test will finish with 
#  # Exception raised while executing Python test script. exception: WindowsError: 32
#  time.sleep(1)
#  
#  cleanup( [ i.name for i in ( f_init_sql, f_init_log, f_init_err, f_meta_init, f_meta_rest, f_meta_diff, f_fblog_before, f_fblog_after, f_validate_log, f_validate_err, f_diff_txt  ) ] + [ tmp_initdb, ]  )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    +	Validation started
    +	Validation finished: 0 errors, 0 warnings, 0 fixed
  """

@pytest.mark.version('>=3.0.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


