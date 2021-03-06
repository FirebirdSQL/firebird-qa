#coding:utf-8
#
# id:           bugs.core_5087
# title:        Database shutdown can cause server crash if multiple attachments run EXECUTE STATEMENT
# decription:   
#                   Test makes two copies of current DB file (and closes db_conn after this):
#                   1) to <db_dml_sessions> - for use by launching ISQL sessions which will perform "heavy DML" (insert rows in the table with wide-key index);
#                   2) to <db_verify_alive> - for use to verify that FB is alive after we change state of <db_dml_sessions> while ISQL sessions running.
#               
#                   Then we establish connect to <db_verify_alive> database (see 'att_chk').
#                   If FB is alive after DML and shutdown then we have to see alive connection to <db_verify_alive>.
#                   If FB works as SuperServer/SuperClassic and crashed then this connect will be lost and test fails with Python exception.
#                   If FB works as Classic then this connect will alive but we can check firebird.log for presense of phrases which testify about crash:
#                   "code attempted to access" and/or "terminate(d) abnormally". We analyze the DIFFERENCE file between old and new firebird.log for this.
#                   
#                   After this, we establish connection to <db_dml_sessions> (see 'att1') and make INSERT statement to special table 't_lock' which has PK-field.
#                   Futher, we launch <PLANNED_DML_ATTACHMENTS> ISQL sessions which also must insert the same (duplicated) key into this table - and they hang.
#                   Table 't_lock' serves as "semaphore": when we close attachment 'att1' then all running ISQL sessions will immediately do their DML job.
#               
#                   We check that all required number connections of ISQLs present by loop in which we query mon$attachments table and count records from it.
#                   When result of this count will be equal to <PLANNED_DML_ATTACHMENTS> then we release lock from T_LOCK table by closing 'att1'.
#               
#                   Futher, we allow ISQL sessions to perform their job by waiting for several seconds and then run command to change DB state to full shutdown.
#                   This command works without returning to caller until all activity in the DB will stop.
#               
#                   When control will return here, we check that attachment 'att_chk' is alive. Also, we get difference of FB log content and parse by searching
#                   phrases which can relate to FB crash.
#               
#                   We also do additional check: all ISQL sessions should be disconnected with writing to logs appropriate messages about shutdown.
#               
#                   Confirmed crash on 3.0.0.31374 Beta1 (Classic).
#                   Hanged on 3.0.0.31896 Beta2 and 3.0.0.32136 RC-1 (no return from SHUTDOWN process).
#                   Parameter 'min_version' was changed to 2.5.9: now is PASSES for normal time (it seems that issues described in CORE-5106 was actually fixed).
#                   Checked 20.08.2020 on:
#                       4.0.0.2170 SS: 13.911s.
#                       4.0.0.2170 CS: 15.915s.
#                       3.0.7.33356 SS: 12.210s.
#                       3.0.7.33356 CS: 15.004s.
#                       2.5.9.27152 SS: 12.690s.
#                       2.5.9.27152 CS: 11.550s.
#                  
#                  OLD COMMENT ABOUT 2.5:
#                  On 2.5 no crash but works VERY slow, even for 5 attachments (checked on WI-V2.5.6.26970, 255 seconds!).
#                  Setting min_version = 2.6.6 is deferred again until CORE-5106 will not be fixed.
#                
# tracker_id:   CORE-5087
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = []

init_script_1 = """
    create sequence g;
    recreate table test(
        id int, 
        s varchar(500) unique, 
        att bigint default current_connection
    );
    recreate table log4attach(
        att bigint default current_connection
        ,dts timestamp default 'now'
        ,process varchar(255)
        ,protocol varchar(255)
        ,address varchar(255)
    );
    commit;

    set term ^;
    execute block as
    begin
        rdb$set_context('USER_SESSION','INITIAL_DDL','1');
    end
    ^
    	
    create or alter trigger trg_attach active on connect position 0 as
    begin
        if ( rdb$get_context('USER_SESSION','INITIAL_DDL') is null )
        then
            in autonomous transaction do 
                insert into log4attach(process,protocol, address)
                values(  rdb$get_context('SYSTEM', 'CLIENT_PROCESS')
                        ,rdb$get_context('SYSTEM', 'NETWORK_PROTOCOL') 
                        ,rdb$get_context('SYSTEM', 'CLIENT_ADDRESS') 
                      );
    end
    ^ -- trg_attach
    set term ;^
    commit;

    create index test_att on test(att);
    create index test_id on test(id);
    create index log4attach_att on log4attach(att);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import subprocess
#  from subprocess import Popen
#  import time
#  import datetime
#  import shutil
#  import difflib
#  import re
#  import fdb
#  
#  PLANNED_DML_ATTACHMENTS = 30
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
#  #---------------------------------------------
#  
#  def svc_get_fb_log( engine, f_fb_log ):
#  
#    global subprocess
#  
#    if engine.startswith('2.5'):
#        get_firebird_log_key='action_get_ib_log'
#    else:
#        get_firebird_log_key='action_get_fb_log'
#  
#    subprocess.call([ context['fbsvcmgr_path'],
#                      "localhost:service_mgr",
#                      get_firebird_log_key
#                    ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#  
#    return
#  
#  #--------------------------------------------
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_file=db_conn.database_name
#  engine = str(db_conn.engine_version)
#  
#  db_conn.close()
#  
#  db_verify_alive="$(DATABASE_LOCATION)tmp_5087_chk4alive.fdb"
#  db_dml_sessions="$(DATABASE_LOCATION)tmp_5087_dml_heavy.fdb"
#  
#  
#  # Copy database to another file in order to make connect to this copy
#  # and check that this connection is alive after we'll do DML and shutdown
#  # with source database (i.e. with "bugs.core_5087.fdb"):
#  shutil.copy2( db_file, db_verify_alive )
#  shutil.copy2( db_file, db_dml_sessions )
#  
#  
#  f_chk_log = open( os.path.join(context['temp_directory'],'tmp_chk_5087.log'), 'w', buffering=0)
#  
#  att_chk = fdb.connect(dsn='localhost:'+db_verify_alive) # This leads to adding 1 row into table 'log4attach'
#  att_chk.execute_immediate('delete from log4attach where att<>current_connection')
#  att_chk.commit()
#  
#  att_chk.begin()
#  cur_chk = att_chk.cursor()
#  
#  cur_chk.execute("select 'check_point_1: established connection to <db_verify_alive>' as msg from rdb$database")
#  f_chk_log.seek(0,os.SEEK_END)
#  for row in cur_chk:
#      f_chk_log.write(row[0])
#  
#  att_chk.commit()
#  
#  att1 = fdb.connect(dsn='localhost:' + db_dml_sessions)
#  att2 = fdb.connect(dsn='localhost:' + db_dml_sessions)
#  
#  att1.execute_immediate('recreate table t_lock(id int primary key)')
#  att1.commit()
#  att1.execute_immediate('insert into t_lock(id) values(1)')
#  
#  # do NOT: att1.close() -- it will be done only after all ISQL sessions will establish their attachments.
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_5087_fblog_before.txt'), 'w', buffering=0)
#  svc_get_fb_log( engine, f_fblog_before )
#  f_fblog_before.close()
#  
#  sql_dml='''
#      commit;
#      set transaction wait;
#      set term ^;
#      execute block as
#      begin
#          insert into t_lock(id) values(1);
#          when any do
#          begin
#           -- nop --
#          end
#      end
#      ^
#      set term ;^
#      commit;
#  
#      set bail on;
#  
#      set transaction read committed;
#      set term ^;
#      execute block as
#          declare n_limit int = 100000;
#          declare s_length smallint;
#      begin
#          select ff.rdb$field_length
#          from rdb$fields ff
#          join rdb$relation_fields rf on ff.rdb$field_name = rf.rdb$field_source
#          where rf.rdb$relation_name=upper('test') and rf.rdb$field_name=upper('s')
#          into s_length;
#  
#          while (n_limit > 0) do
#          begin
#              execute statement ('insert into test(id, s) values( ?, ?)')
#                    ( gen_id(g,1), rpad('', :s_length, uuid_to_char(gen_uuid()))  )
#                    with autonomous transaction
#              ;
#  
#              n_limit = n_limit - 1;
#          end
#          insert into test( id ) values( -current_connection );
#      end
#      ^
#      set term ;^
#      commit;
#  '''
#  
#  f_dml_sql = open( os.path.join(context['temp_directory'],'tmp_dml_5087.sql'), 'w')
#  f_dml_sql.write(sql_dml)
#  flush_and_close( f_dml_sql )
#  
#  f_list = []
#  p_list = []
#  
#  ########################################################
#  #  Launching dozen of child ISQL processes with doing ES
#  ########################################################
#  
#  for i in range(0, PLANNED_DML_ATTACHMENTS):
#      sqllog=open( os.path.join(context['temp_directory'],'tmp_dml_5087_'+str(i)+'.log'), 'w')
#      f_list.append(sqllog)
#  
#  for i in range(len(f_list)):
#      ###########################################
#      #   a s y n c h r o n o u s     l a u n c h
#      ###########################################
#      p_isql=Popen( [ context['isql_path'], 'localhost:' + db_dml_sessions, "-i", f_dml_sql.name ],
#                    stdout=f_list[i],
#                    stderr=subprocess.STDOUT
#                  )
#      p_list.append(p_isql)
#  
#  cur2 = att2.cursor()
#  while True:
#     att2.begin()
#     cur2.execute("select count(*) from mon$attachments a where a.mon$attachment_id<>current_connection and a.mon$remote_process containing 'isql'")
#     for r in cur2:
#         established_dml_attachments = r[0]
#     att2.commit()
#  
#     if established_dml_attachments < PLANNED_DML_ATTACHMENTS:
#         # do not delete, leave it for debug:
#         ####################################
#         #msg = datetime.datetime.now().strftime("%H:%M:%S.%f") + ' LOOP: only %(established_dml_attachments)s attachments exist of planned %(PLANNED_DML_ATTACHMENTS)s' % locals() 
#         #print( msg )
#         #f_chk_log.write('\\n')
#         #f_chk_log.write(msg)
#         time.sleep(0.2)
#         continue
#     else:
#         # do not delete, leave it for debug:
#         ####################################
#         #msg = datetime.datetime.now().strftime("%H:%M:%S.%f") + ' Found all planned %(PLANNED_DML_ATTACHMENTS)s attachments. Can release lock.' % locals() 
#         msg = 'Found all attachments of planned number to <db_dml_sessions>. No we can release lock for allow them to start DML.'
#         #print( msg )
#         f_chk_log.write('\\n\\n')
#         f_chk_log.write(msg)
#         break
#  
#  cur2.close()
#  att2.close()
#  
#  #-----------------------------------
#  
#  # release t_lock record.
#  # All launched ISQL sessions can do useful job (INSERT statements) since this point.
#  att1.close()
#  
#  # Let ISQL sessions do some work:
#  time.sleep( 3 )
#  
#  cur_chk.execute("select 'check_point_2: before shutdown <db_dml_sessions>' as msg from rdb$database")
#  f_chk_log.seek(0,os.SEEK_END)
#  for row in cur_chk:
#      f_chk_log.write('\\n')
#      f_chk_log.write(row[0])
#  
#  f_shutdown_log = open( os.path.join(context['temp_directory'],'tmp_shutdown_5087.log'), 'w', buffering=0)
#  
#  ####################################
#  # S H U T D O W N    D A T A B A S E
#  ####################################
#  
#  subprocess.call( [context['fbsvcmgr_path'],"localhost:service_mgr",
#                    "action_properties",
#                    "dbname", db_dml_sessions,
#                    "prp_shutdown_mode", "prp_sm_full", "prp_force_shutdown", "0"
#                   ],
#                   stdout=f_shutdown_log,
#                   stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_shutdown_log )
#  
#  cur_chk.execute("select 'check_point_3: after shutdown <db_dml_sessions>' as msg from rdb$database")
#  f_chk_log.seek(0,os.SEEK_END)
#  for row in cur_chk:
#      f_chk_log.write('\\n')
#      f_chk_log.write(row[0])
#  
#  #------------------------------------------
#  for i in range(len(f_list)):
#      flush_and_close( f_list[i] )
#  
#  for i in range(len(p_list)):
#      p_list[i].terminate()
#  
#  #------------------------------------------
#  
#  cur_chk.execute("select 'check_point_4: killed all DML sessions.' as msg from rdb$database")
#  f_chk_log.seek(0,os.SEEK_END)
#  for row in cur_chk:
#      f_chk_log.write('\\n')
#      f_chk_log.write(row[0])
#  
#  # Here we must wait a little because firebird.log will get new messages NOT instantly.
#  time.sleep(3)
#  
#  crashes_in_worker_logs = 0
#  for i in range(len(f_list)):
#      dml_worker_log=open(f_list[i].name).read()
#      if 'SQLSTATE = 08004' in dml_worker_log: #### do NOT add >>> or 'SQLSTATE = 08006' in dml_worker_log:
#          crashes_in_worker_logs += 1
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_5087_fblog_after.txt'), 'w', buffering=0)
#  svc_get_fb_log( engine, f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  att_chk.begin()
#  cur_chk.execute("select 'check_point_5: get firebird.log' as msg from rdb$database")
#  f_chk_log.seek(0,os.SEEK_END)
#  for row in cur_chk:
#      f_chk_log.write('\\n')
#      f_chk_log.write(row[0])
#  
#  cur_chk.execute('select count(distinct att) from log4attach;')
#  for row in cur_chk:
#      f_chk_log.write('\\n')
#      f_chk_log.write('distinct attachments to <db_verify_alive>: '+str(row[0])) # must be 1
#  
#  cur_chk.close()
#  att_chk.close()
#  
#  #os.remove(db_verify_alive)
#  
#  #------------------------------------------
#  
#  f_chk_log.seek(0,os.SEEK_END)
#  f_chk_log.write('\\n')
#  f_chk_log.write('Found crash messages in DML worker logs: %(crashes_in_worker_logs)s' % locals() ) # must be 0.
#  
#  sql_chk='''
#      set list on;
#      select
#         iif(  count(distinct t.att) = %(PLANNED_DML_ATTACHMENTS)s
#              ,'YES'
#              ,'NO. Only ' || count(distinct t.att) || ' attachments of planned %(PLANNED_DML_ATTACHMENTS)s established.' )
#         as "All DML sessions found in DB ?"
#      from rdb$database r
#      left join (
#          select 
#              att
#              ,count( iif(id >=0, id, null) ) as cnt_in_autonom_tx
#              ,count( iif(id < 0, id, null) ) as cnt_in_common_tx
#          from test 
#          group by att
#      ) t on t.cnt_in_common_tx = 0 and t.cnt_in_autonom_tx > 0
#      ;
#  ''' % locals()
#  
#  f_chk_sql = open( os.path.join(context['temp_directory'],'tmp_chk_5087.sql'), 'w', buffering=0)
#  f_chk_sql.write(sql_chk)
#  f_chk_sql.close()
#  
#  f_chk_log.seek(0,os.SEEK_END)
#  
#  f_chk_log.write('\\n')
#  f_chk_log.write('Point before bring DML database online.' )
#  
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_db_online",
#                    "dbname", db_dml_sessions,
#                   ]
#                 )
#  
#  f_chk_log.write('\\n')
#  f_chk_log.write('Point after bring DML database online.' )
#  
#  subprocess.call( [ context['isql_path'], "localhost:"+db_dml_sessions, "-nod", "-i", f_chk_sql.name ],
#                    stdout=f_chk_log,
#                    stderr=subprocess.STDOUT
#                  )
#  flush_and_close( f_chk_log )
#  
#  #-------------------------------------------
#  
#  # Now we can compare two versions of firebird.log and check their difference.
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_5087_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  allowed_patterns = (
#       re.compile('code attempt\\S+.*\\s+access',re.IGNORECASE),
#       re.compile('terminate\\S+ abnormally',re.IGNORECASE),
#       re.compile('Error writing data',re.IGNORECASE)
#  )
#  
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+'):
#              match2some = filter( None, [ p.search(line) for p in allowed_patterns ] )
#              if match2some:
#                  print('Crash message in firebird.log detected: '+line.upper())
#  
#  # This should be empty:
#  #######################
#  with open( f_shutdown_log.name,'r') as f:
#      for line in f:
#          print(line.upper())
#  
#  
#  # Print check info:
#  with open( f_chk_log.name,'r') as f:
#    print( f.read() )
#  
#  
#  ###############################
#  # Cleanup.
#  k_list = [ x.name for x in [ f_shutdown_log, f_dml_sql, f_chk_sql, f_fblog_before, f_fblog_after, f_diff_txt, f_chk_log] + f_list ]
#  k_list += [db_verify_alive, db_dml_sessions]
#  cleanup(k_list)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    check_point_1: established connection to <db_verify_alive>
    Found all attachments of planned number to <db_dml_sessions>. No we can release lock for allow them to start DML.
    check_point_2: before shutdown <db_dml_sessions>
    check_point_3: after shutdown <db_dml_sessions>
    check_point_4: killed all DML sessions.
    check_point_5: get firebird.log
    distinct attachments to <db_verify_alive>: 1
    Found crash messages in DML worker logs: 0
    Point before bring DML database online.
    Point after bring DML database online.
    All DML sessions found in DB ?  YES
  """

@pytest.mark.version('>=2.5.9')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


