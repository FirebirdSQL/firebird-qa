#coding:utf-8

"""
ID:          issue-3690
ISSUE:       3690
TITLE:       Ability to cancel waiting in lock manager
DESCRIPTION:
  Fully reimplemented 10.01.2020. Reason: ISQL-"killer" could not find record in
  mon$attachments that should be deleted.

  Test asynchronously launches ISQL with script that will hang because of two concurrent
  attachments trying to update the same record (second attachment is created using ES/EDS).
  After this we have to launch second instance of ISQL which will attempt to kill both
  connections created in the 1st ISQL.

  The *most* problem here is properly determine time that we have to wait until 1st ISQL
  will really establish its connect! If this time is too short then second ISQL ("killer")
  will NOT able to see 1st ISQL in mon$attachments and will not be able to delete (because
  there will be NOT YET attachment to delete!). This mean that 2nd ISQL will finish without
  really check that it could kill hanged attachments. Test in this case will not finish if
  1st ISQL uses tx with infinite WAIT!

  To be sure that 2nd ISQL ("killer") will be able to see 1st one ("hanged") we have to
  make pretty long PSQL-loop which tries to find any record in mon$attachment that is from
  concurrent connection (which user name we know for advance: 'tmp$c3323').
  This PSQL loop must finish as fast as we find record that will be then deleted.

  Lot of runs show that there is a problem in 4.0.0 Classic: it requires too long time in
  PSQL loop to find such attachment. Time in 4.0 CS can be about 1-2 seconds and number of
  iterations will be greater than 100. No such problem in all 3.0 and in 4.0 for other modes.
notes:
[24.12.2020]
  Waiting for completion of child ISQL async process is done by call <isql_PID>.wait()
  instead of old (and "fragile") assumption about maximal time that it could last before
  forcedly terminate it.
[17.11.2021]
  This test is too complicated and fragile (can screw the test environment)
  It should be reimplemnted in more robust way, or removed from suite
JIRA:        CORE-3323
"""

import pytest
from firebird.qa import *

substitutions = [('Data source : Firebird::localhost:.*', 'Data source : Firebird::localhost'),
                   ('After line.*', ''), ('.*Killed by database administrator.*', ''),
                   ('-At block line:.*', '-At block line'),
                   ('Execute statement error at isc_dsql_(execute2|prepare)', 'Execute statement error at isc_dsql')]

db = db_factory()


act = python_act('db', substitutions=substitutions)

expected_stdout = """
    Point_A:                        starting EB with lock-conflict
    id_at_point_A:                  -1
    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_execute2 :
    335544856 : connection shutdown
    Statement : update test set id = - (1000 + id)
    Data source : Firebird::localhost
    -At block line
    Point_B                         finished EB with lock-conflict
    id_at_point_B:                  -1
    point_C:                        Intro script that must kill other attachment
    point_D:                        starting kill hanged connection
    id_at_point_D:                  1
    ATTACHMENT_TO_BE_KILLED         <EXPECTED: NOT NULL>
    point_E:                        Running delete from mon$attachments statement
    Records affected: 1
    point_F:                        Reconnect and look for attachment of other user
    id_at_point_F:                  1
    STILL_ALIVE_ATTACHMENT_ID       <EXPECTED: NULL>
    pointG:                         finished kill hanged connection
"""

@pytest.mark.skip("Test fate to be determined")
@pytest.mark.version('>=3')
def test_1(act: Action):
    pytest.skip("Test not IMPLEMENTED")


# test_script_1
#---
# import os
#  import subprocess
#  from subprocess import Popen
#  import time
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
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#
#  #--------------------------------------------
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  clear_ext_pool_statement=''
#  usr_plugin_clause=''
#
#  if db_conn.engine_version >= 4.0:
#      clear_ext_pool_statement = 'ALTER EXTERNAL CONNECTIONS POOL CLEAR ALL;'
#
#  if db_conn.engine_version >= 3.0:
#      # usr_plugin_clause='using plugin Legacy_userManager'
#      usr_plugin_clause='using plugin Srp'
#
#  db_conn.close()
#
#
#  init_ddl='''
#      set term ^;
#      execute block as
#      begin
#          begin
#              execute statement 'drop user tmp$c3323 %(usr_plugin_clause)s' with autonomous transaction;
#              when any do begin end
#          end
#      end^
#      set term ;^
#      commit;
#
#      create user tmp$c3323 password '456' %(usr_plugin_clause)s;
#      commit;
#
#      recreate table test(id int);
#      commit;
#      insert into test values(1);
#      commit;
#
#      grant select,update on test to tmp$c3323;
#      commit;
#  ''' % locals()
#
#  runProgram('isql', [dsn], init_ddl)
#
#
#  lock_sql='''
#      set list on;
#      commit;
#      set transaction wait;
#
#      update test set id = -id;
#      select 'starting EB with lock-conflict' as "Point_A:" --------------  p o i n t   [ A ]
#            ,id as "id_at_point_A:"
#      from test;
#
#      set term ^;
#      execute block as
#      begin
#          -- This statement will for sure finish with exception, but
#          -- in 2.5.0 it will be 'lock-conflict' (and this was WRONG),
#          -- while on 2.5.1 and above it should be 'connection shutdown'.
#
#          -- 11.05.2017, FB 4.0 only!
#          -- Following messages can appear after 'connection shutdown'
#          -- (letter from dimitr, 08-may-2017 20:41):
#          --   isc_att_shut_killed: Killed by database administrator
#          --   isc_att_shut_idle: Idle timeout expired
#          --   isc_att_shut_db_down: Database is shutdown
#          --   isc_att_shut_engine: Engine is shutdown
#
#          execute statement 'update test set id = - (1000 + id)'
#              on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
#              as user 'TMP$C3323' password '456';
#      end
#      ^
#      set term ;^
#
#      select 'finished EB with lock-conflict' as "Point_B" --------------  p o i n t   [ B ]
#            ,id as "id_at_point_B:"
#      from test;
#      rollback;
#  '''
#
#  f_hanged_sql=open( os.path.join(context['temp_directory'],'tmp_3323_hang.sql'), 'w')
#  f_hanged_sql.write(lock_sql)
#  f_hanged_sql.close()
#
#  f_hanged_log=open( os.path.join(context['temp_directory'],'tmp_3323_hang.log'), "w", buffering = 0)
#
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  p_hanged_isql = Popen([context['isql_path'], dsn, "-ch", 'utf8', "-i" , f_hanged_sql.name],stdout=f_hanged_log, stderr=subprocess.STDOUT)
#
#  usr=user_name
#  pwd=user_password
#
#  # Limit: how long "killer" must wait until "victim" will establish its connect, milliseconds.
#  # It was encountered on Classic that this time can be valueable if heavy concurrent workload
#  # presents on host where tests run:
#  ###############################################
#  MAX_WAIT_FOR_VICTIM_ESTABLISH_ITS_CONNECT=15000
#  ###############################################
#
#  killer_script='''
#      set list on;
#
#      select 'Intro script that must kill other attachment' as "point_C:" ------------------  p o i n t   [ C ]
#      from test;
#
#      set term ^;
#      execute block returns( found_other_attach_for_attempts int, found_other_attach_for_ms int ) as
#          declare c smallint = 0;
#          declare t timestamp;
#      begin
#          found_other_attach_for_attempts = 0;
#          t = 'now';
#          while (c = 0) do
#          begin
#              found_other_attach_for_attempts = found_other_attach_for_attempts + 1;
#              in autonomous transaction do
#                  select count(*)
#                  from (
#                      select mon$attachment_id
#                      from mon$attachments a
#                      where mon$user = upper('TMP$C3323' )
#                      rows 1
#                  )
#                  into c;
#              found_other_attach_for_ms = datediff(millisecond from t to cast('now' as timestamp));
#              if (found_other_attach_for_ms > %(MAX_WAIT_FOR_VICTIM_ESTABLISH_ITS_CONNECT)s ) then
#              begin
#                  suspend; -- output found_other_attach_for_attempts and found_other_attach_for_ms
#                  --######
#                  leave;
#                  --######
#              end
#          end
#      end
#      ^
#      set term ;^
#      rollback;
#
#
#      select 'starting kill hanged connection' as "point_D:" ------------------  p o i n t   [ D ]
#            ,id as "id_at_point_D:"
#      from test;
#
#      select iif( a.mon$attachment_id is not null, '<EXPECTED: NOT NULL>', '### UNEXPECTED: NULL ###' ) as attachment_to_be_killed
#      from rdb$database
#      left join mon$attachments a on mon$user = upper('TMP$C3323' )
#      ;
#
#      select 'Running delete from mon$attachments statement'  as "point_E:" ------------------  p o i n t   [ E ]
#      from rdb$database;
#
#      set count on;
#      delete from mon$attachments
#      where mon$user = upper('TMP$C3323' )
#      ;
#      set count off;
#      commit;
#
#      connect '$(DSN)' user '%(usr)s' password '%(pwd)s';
#
#      %(clear_ext_pool_statement)s
#
#      select 'Reconnect and look for attachment of other user' as "point_F:" ------------------  p o i n t   [ F ]
#            ,id as "id_at_point_F:"
#      from test;
#
#      select iif( a.mon$attachment_id is null, '<EXPECTED: NULL>', '### UNEXPECTED NOT NULL: attach_id=' || a.mon$attachment_id || '; state=' || coalesce(a.mon$state, '<null>') || ' ###' ) as still_alive_attachment_id
#      from rdb$database r
#      left join mon$attachments a on a.mon$user = upper('TMP$C3323');
#      commit;
#
#      set blob all;
#
#      select a.*, s.*
#      from mon$attachments a left join mon$statements s using(mon$attachment_id)
#      where a.mon$user = upper('TMP$C3323')
#      ;
#
#      select 'finished kill hanged connection' as "pointG:"  -----------------  p o i n t   [ G ]
#      from rdb$database;
#      commit;
#
#      drop user tmp$c3323 %(usr_plugin_clause)s;
#      commit;
#
#  ''' % locals()
#
#
#  f_killer_sql=open( os.path.join(context['temp_directory'],'tmp_3323_kill.sql'), 'w')
#  f_killer_sql.write(killer_script)
#  flush_and_close(f_killer_sql)
#
#
#  # starting ISQL-KILLER:
#  #######################
#
#  f_killer_log=open( os.path.join(context['temp_directory'],'tmp_3323_kill.log'), "w", buffering = 0)
#  subprocess.call( [context['isql_path'], dsn, "-ch", "utf8", "-i" , f_killer_sql.name],stdout=f_killer_log, stderr=subprocess.STDOUT )
#  flush_and_close(f_killer_log)
#
#  # :::::::::::::::::::::::::::::::::::::::::::::
#  # :::             A.C.H.T.U.N.G             :::
#  # ::: DO NOT call p_hanged_isql.terminate() :::
#  # :::::::::::::::::::::::::::::::::::::::::::::
#  # Here we must W.A.I.T until ISQL-victim (which just has been killed) finished
#  # with raising exception ("SQLSTATE = 42000 / connection shutdown") and fully
#  # flushes its log on disk.
#
#  # Wait until ISQL complete its mission:
#  p_hanged_isql.wait()
#
#  flush_and_close(f_hanged_log)
#
#  with open( f_hanged_log.name,'r') as f:
#      print(f.read())
#
#  with open( f_killer_log.name,'r') as f:
#      print(f.read())
#
#
#  # We have to change DB state to full shutdown in order to prevent "Object in use"
#  # while fbtest will try to drop these databases (set linger = 0 does not help!)
#  ###############################################################################
#  runProgram('gfix',[dsn,'-shut','full','-force','0'])
#  runProgram('gfix',[dsn,'-online'])
#
#  # CLEANUP
#  #########
#  f_list=(f_hanged_sql,f_killer_sql,f_killer_log,f_hanged_log)
#  cleanup( [f.name for f in f_list] )
#
#
#---
