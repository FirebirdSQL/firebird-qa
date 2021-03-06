#coding:utf-8
#
# id:           bugs.core_4707
# title:        Implement ability to validate tables and indices online (without exclusive access to database)
# decription:   
#                   Checked on: 4.0.0.1635 SS: 7.072s; 4.0.0.1633 CS: 7.923s; 3.0.5.33180 SS: 6.599s; 3.0.5.33178 CS: 7.189s. 2.5.9.27119 SS: 5.951s; 2.5.9.27146 SC: 5.748s.
#                
# tracker_id:   CORE-4707
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.5
# resources: None

substitutions_1 = [('[\\d]{2}:[\\d]{2}:[\\d]{2}.[\\d]{2}', ''), ('Relation [\\d]{3,4}', 'Relation')]

init_script_1 = """
    set term ^;
    execute block as
    begin
        execute statement 'drop sequence g';
    when any do begin end
    end^
    set term ;^
    commit;
    create sequence g;
    commit;
    recreate table test1(id int, s varchar(1000));
    recreate table test2(id int primary key using index test2_pk, s varchar(1000), t computed by (s) );
    recreate table test3(id int);
    commit;
    
    insert into test1(id, s) select gen_id(g,1), rpad('', 1000, gen_id(g,0) ) from rdb$types rows 100;
    insert into test2(id, s) select id, s from test1;
    commit;
    
    create index test2_s on test2(s);
    create index test2_c on test2 computed by(s);
    create index test2_t on test2 computed by(t);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import subprocess
#  from subprocess import Popen
#  import time
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  # Obtain engine version:
#  engine = str(db_conn.engine_version) # convert to text because 'float' object has no attribute 'startswith'
#  db_file = db_conn.database_name
#  db_conn.close()
#  
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
#  #--------------------------------------------
#  
#  
#  # Following script will hang for sevral seconds (see 'lock timeout' argument - and this will serve as pause
#  # during which we can launch fbsvcmgr to validate database:
#  lock_sql='''
#      set term ^;
#      execute block as
#      begin
#        execute statement 'drop role tmp$r4707';
#        when any do begin end
#      end ^
#      set term ;^
#      commit;
#  
#      set transaction wait;
#  
#      delete from test1;
#      insert into test3(id) values(1);
#      set list on;
#      select 'Starting EB with infinite pause.' as isql_msg from rdb$database;
#      set term ^;
#      execute block as
#      begin
#        execute statement 'update test1 set id=-id'
#        on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
#        as user '%s' password '%s'
#           role 'TMP$R4707' -- this will force to create new attachment, and its Tx will be paused on INFINITE time.
#        ;
#        when any do begin end
#      end ^
#      set term ;^
#      select 'EB with pause finished.' as msg_2 from rdb$database;
#  ''' % (user_name, user_password)
#  
#  f_hang_sql=open( os.path.join(context['temp_directory'],'tmp_4707_hang.sql'), 'w')
#  f_hang_sql.write(lock_sql)
#  flush_and_close( f_hang_sql )
#  
#  
#  ################ ##############################################################################
#  # Make asynchronous call of ISQL which will stay several seconds in pause due to row-level lock
#  # #############################################################################################
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  f_hang_log=open( os.path.join(context['temp_directory'],'tmp_4707_hang.log'), 'w')
#  p_hang = Popen([context['isql_path'], dsn, "-i", f_hang_sql.name],stdout=f_hang_log, stderr=subprocess.STDOUT)
#  
#  # Here we should wait while ISQL will establish its connect (in separate child window, call asynchronous) and 
#  # stay in pause:
#  time.sleep(2)
#  
#  #############################################################################################
#  # Make SYNC. call of fbsvcmgr in order to validate database which has locks on some relations
#  #############################################################################################
#  f_svc_log=open( os.path.join(context['temp_directory'],'tmp_4707_svc.log'), 'w')
#  subprocess.call([ context['fbsvcmgr_path'], 'localhost:service_mgr','action_validate','dbname', db_file,'val_lock_timeout','1'],stdout=f_svc_log, stderr=subprocess.STDOUT)
#  flush_and_close( f_svc_log )
#  
#  #######################################################
#  # TERMINATE separate (child) process of ISQL that hangs
#  #######################################################
#  p_hang.terminate()
#  flush_and_close( f_hang_log )
#  
#  with open( f_hang_log.name,'r') as f:
#      print(f.read())
#  
#  with open( f_svc_log.name,'r') as f:
#      print(f.read())
#  
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( [i.name for i in (f_hang_sql, f_hang_log, f_svc_log) ] )
#  
#  ##                                    ||||||||||||||||||||||||||||
#  ## ###################################|||  FB 4.0+, SS and SC  |||##############################
#  ##                                    ||||||||||||||||||||||||||||
#  ## If we check SS or SC and ExtConnPoolLifeTime > 0 (config parameter FB 4.0+) then current
#  ## DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
#  ## will not able to drop this database at the final point of test.
#  ## Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
#  ## we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
#  ## in the letter to hvlad and dimitr 13.10.2019 11:10).
#  ## This means that one need to kill all connections to prevent from exception on cleanup phase:
#  ## SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
#  ## #############################################################################################
#  con4cleanup=fdb.connect( dsn = dsn, user = user_name, password = user_password )
#  con4cleanup.execute_immediate('delete from mon$attachments where mon$attachment_id != current_connection')
#  con4cleanup.commit()
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ISQL_MSG                        Starting EB with infinite pause.
    08:37:01.14 Validation started
    08:37:01.15 Relation 128 (TEST1)
    08:37:02.15 Acquire relation lock failed
    08:37:02.15 Relation 128 (TEST1) : 1 ERRORS found
    08:37:02.15 Relation 129 (TEST2)
    08:37:02.15   process pointer page    0 of    1
    08:37:02.15 Index 1 (TEST2_PK)
    08:37:02.15 Index 2 (TEST2_S)
    08:37:02.15 Index 3 (TEST2_C)
    08:37:02.15 Index 4 (TEST2_T)
    08:37:02.17 Relation 129 (TEST2) is ok
    08:37:02.17 Relation 130 (TEST3)
    08:37:03.17 Acquire relation lock failed
    08:37:03.17 Relation 130 (TEST3) : 1 ERRORS found
    08:37:03.17 Validation finished
  """

@pytest.mark.version('>=2.5.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


