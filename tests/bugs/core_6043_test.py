#coding:utf-8
#
# id:           bugs.core_6043
# title:        GTTs do not release used space
# decription:   
#                   === For FB 3.x ===
#                       Test obtains full path to $fb_home via FBSVCMGR info_get_env.
#                       Then it makes copy of file 'databases.conf' that is in $fb_home directory because 
#                       following lines will be added to that 'databases.conf':
#                       ===
#                       tmp_6043_keep = ...
#                       {
#                           ClearGTTAtRetaining = 0
#                       }
#                       After this, it does connect to this alias and run statements from ticket with commit/rollback retain.
#                       We check that:
#                         * COMMIT RETAIN preserves record that was inserted in the statement before this commit;
#                         * ROLLBACK RETAIN does NOT delete record that was inserted before COMMIT RETAIN.
#               
#                       Then we check the same for ClearGTTAtRetaining = 1 (i.e. for default value) - just to ensure that it works.
#                       Finally, previous databases.conf file is restored in initial state.
#               
#                   === For FB 4.x ===
#                       It is enough just to run ISQL; databases.conf can be left unchanged.
#               
#                   13.12.2019.
#                   It seems that we have to DISABLE BUFFERING in any IO operation which relates to preparing scripts, configs or logs.
#                   Otherwise sporadic runtime errors can occur: I/O error during "CreateFile (open)" operation for file "..."
#               
#                   Explanation:
#                   https://docs.python.org/2/library/functions.html#open
#                   https://stackoverflow.com/questions/18984092/python-2-7-write-to-file-instantly/41506739
#               
#                   Checked on:
#                       4.0.0.1687 SS: 1.536s.
#                       4.0.0.1685 CS: 2.026s.
#                       3.0.5.33207 SS: 1.435s.
#                       3.0.5.33152 SC: 1.243s.
#                       3.0.5.33206 CS: 2.626s.
#                
# tracker_id:   CORE-6043
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import subprocess
#  import time
#  import shutil
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  this_db = db_conn.database_name
#  db_conn.close()
#  
#  svc = services.connect(host='localhost', user= user_name, password= user_password)
#  fb_home = svc.get_home_directory()
#  svc.close()
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
#  tmp_fdb_keep=os.path.join(context['temp_directory'],'tmp_6043.keep_GTT_data.fdb')
#  tmp_fdb_kill=os.path.join(context['temp_directory'],'tmp_6043.kill_GTT_data.fdb')
#  
#  shutil.copy2( this_db, tmp_fdb_keep )
#  shutil.copy2( this_db, tmp_fdb_kill )
#  
#  dbconf = os.path.join( fb_home, 'databases.conf')
#  dbcbak = os.path.join( fb_home, 'databases.bak')
#  
#  # Resut: fb_home is full path to FB instance home (with trailing slash).
#  shutil.copy2( dbconf, dbcbak )
#  
#  # ----------------------------------------------------------------------
#  
#  isql_script='''
#      set list on;
#  
#      recreate global temporary table gtt (id int) on commit delete rows;
#      commit;
#  
#      set count off;
#      insert into gtt values (3);
#      commit retain;
#  
#      set count on;
#      select * from gtt; -- point 1
#  
#      set count off;
#      insert into gtt values (4);
#      rollback retain;
#  
#      set count on;
#      select * from gtt; -- point 2
#  '''
#  
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_isql_6043.sql'), 'w')
#  f_isql_cmd.write( isql_script )
#  flush_and_close( f_isql_cmd )
#  
#  # --------------------------------------------------------------------
#  
#  f_dbconf=open( dbconf,'a')
#  f_dbconf.seek(0, 2)
#  
#  alias_data='''
#  
#      # Created temply by fbtest, CORE-6043. Should be removed auto.
#      # WARNING! DO NOT ADD YET ANOTHER ALIAS FOR THE SAME DATABASE!
#      # Attempt to connect to any of these aliases will fail with message:
#      # =======
#      #   Statement failed, SQLSTATE = 08004
#      #   Server misconfigured - contact administrator please
#      # =======
#      # Server log will contain:
#      # File databases.conf contains bad data: Duplicated configuration for database <file>
#  
#      tmp_6043_keep = %(tmp_fdb_keep)s
#      {
#          # Value of 0 makes engine to not clear GTT data on COMMIT/ROLLBACK RETAINING and let application to see it.
#          # Default value is 1 (clear GTT data on commit/rollback retaining).
#          # Note: in Firebird 4 default value will be changed to 0 and this setting will
#          # be removed at Firebird 5.
#          ClearGTTAtRetaining = 0
#      }
#  
#      tmp_6043_kill = %(tmp_fdb_kill)s
#      {
#          # Check that 1 really works as default value, i.e. clears GTT data on commit/rollback retaining.
#          ClearGTTAtRetaining = 1
#      }
#  
#  
#  ''' % locals()
#  
#  f_dbconf.write(alias_data)
#  flush_and_close( f_dbconf )
#  
#  # 4debug: shutil.copy2( fb_home+'databases.conf', fb_home+'databases.conf.check_it' )
#  
#  # NB: buffering = 0 - we want this file be immediately on disk after closing in order to avoid excessive waiting for it
#  ###################
#  f_isql_keep_log=open( os.path.join(context['temp_directory'],'tmp_6043.keep_GTT_data.log'), 'w')
#  subprocess.call([ context['isql_path'], 'localhost:tmp_6043_keep',  "-q", "-i", f_isql_cmd.name], stdout=f_isql_keep_log, stderr=subprocess.STDOUT)
#  flush_and_close( f_isql_keep_log )
#  
#  with open( f_isql_keep_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              print( 'When ClearGTTAtRetaining = 0: ' + line )
#  
#  ####################################################################
#  
#  # NB: buffering = 0 - we want this file be immediately on disk after closing in order to avoid excessive waiting for it
#  f_isql_kill_log=open( os.path.join(context['temp_directory'],'tmp_6043.kill_GTT_data.log'), 'w')
#  subprocess.call([context['isql_path'], 'localhost:tmp_6043_kill',  "-q", "-i", f_isql_cmd.name], stdout=f_isql_kill_log, stderr=subprocess.STDOUT)
#  flush_and_close( f_isql_kill_log )
#  
#  with open( f_isql_kill_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              print( 'When ClearGTTAtRetaining = 1: ' + line )
#  
#  ####################################################################
#  
#  # Restore previous content:
#  shutil.move( dbcbak, dbconf )
#  
#  #####################################################################
#  # Cleanup:
#  time.sleep(1)
#  cleanup( ( f_isql_keep_log, f_isql_kill_log, f_isql_cmd, tmp_fdb_keep, tmp_fdb_kill ) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    When ClearGTTAtRetaining = 0: ID 3
    When ClearGTTAtRetaining = 0: Records affected: 1
    When ClearGTTAtRetaining = 0: ID 3
    When ClearGTTAtRetaining = 0: Records affected: 1

    When ClearGTTAtRetaining = 1: Records affected: 0
    When ClearGTTAtRetaining = 1: Records affected: 0
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


# version: 4.0
# resources: None

substitutions_2 = [('[ \t]+', ' ')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;

    recreate global temporary table gtt (id int) on commit delete rows;
    commit;

    set count off;
    insert into gtt values (4);
    commit retain;

    set count on;
    select * from gtt; -- point 1

    set count off;
    insert into gtt values (5);
    rollback retain;

    set count on;
    select * from gtt; -- point 2
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    ID 4
    Records affected: 1

    ID 4
    Records affected: 1
  """

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

