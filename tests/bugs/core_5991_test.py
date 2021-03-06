#coding:utf-8
#
# id:           bugs.core_5991
# title:        Trace could not work correctly with quoted file names in trace configurations
# decription:   
#                   Thank Vlad for suggestions.
#               
#                   NOTE-1. Bug will NOT appear if PATTERN is used in database-section!
#                   In order to reproduce bug one need to create config file for trace with following 
#                   _SINGLE_ file name in databases-section:
#                   =====
#                       database = 'C:\\FBTESTING\\qa
#               bt-repo	mp	mp_5991.o'clock.fdb'
#                       {
#                           enabled = true
#                           time_threshold = 0 
#                           log_initfini = false
#                           log_connections = true
#                           log_transactions = true
#                           log_statement_finish = true
#                       }
#                   =====
#                   (path 'C:\\FBTESTING\\qa
#               bt-repo	mp' will be replaced with actual test DB location)
#               
#                   Then we start trace session.
#               
#                   NOTE-2: if this trace session will be forced to wait about 10 seconds, then error message will appear
#                   with text "error while parsing trace configuration" but DB name will be securityN.fdb. 
#                   Moreover, an operation with any DB which has name different than specified in database-section will
#                   raise this error, and its text can be misleading that trace did not started at all or was terminated.
#                   This is because another bug (not yet fixed) which Vlad mentioned privately in letter 26.02.19 23:37.
#                   
#                   :::: NB :::::
#                   We can IGNORE this error message despite it contains phrase "Error creating trace session" and go on.
#                   Trace session actually *WILL* be created and we have to check this here by further actions with DB.
#                   :::::::::::::
#                   
#                   After this, we create database with the same name by calling fdb.create_database().
#                   NOTE-3: we have to enclose DB file in double quotes and - moreover - duplicate single apostoph,
#                   otherwise fdb driver will create DB without it, i.e.: "tmp_5991.oclock.fdb".
#               
#                   At the second step we do trivial statement and drop this database (tmp_5991.o'clock.fdb).
#                   Finally, we wait at least two seconds because trace buffer must be flushed to disk, stop trace session
#                   and then - open trace log for parsing it.
#                   Trace log MUST contain all of following phrases (each of them must occur in log at least one time):
#                       1. Trace session ID <N> started
#                       2. CREATE_DATABASE
#                       3. START_TRANSACTION
#                       4. EXECUTE_STATEMENT_FINISH
#                       5. ROLLBACK_TRANSACTION
#                       6. DROP_DATABASE
#                   We check each line of trace for matching to patterns (based on these phrases) and put result into Python dict.
#                   Resulting dict must contain 'FOUND' and value for every of its keys (patterns).
#               
#                   Confirmed bug on 3.0.4.33054.
#                   01-mar-2021: adapted for work on Linux.
#                   Checked on 4.0.0.2377 and 3.0.8.33415 (both Windows and Linux).
#               
#                
# tracker_id:   CORE-5991
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = [('Trying to create.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import re
#  import time
#  import subprocess
#  from subprocess import Popen
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  fdb_file=os.path.join( '$(DATABASE_LOCATION)', "tmp_5991.o'clock.fdb" )
#  db_conn.close()
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
#  cleanup( fdb_file, )
#  
#  if os.name == 'nt':
#      fdb_trace = fdb_file.replace('/','\\\\')
#  else:
#      fdb_trace = fdb_file
#  
#  #####################################################################
#  # Prepare config for trace session that will be launched by call of FBSVCMGR:
#  
#  txt = '''    database = '%(fdb_trace)s'
#      {
#          enabled = true
#          time_threshold = 0 
#          log_initfini = false
#          log_connections = true
#          log_transactions = true
#          log_statement_finish = true
#      }
#  ''' % locals()
#  
#  trc_cfg=open( os.path.join(context['temp_directory'],'tmp_trace_5991.cfg'), 'w')
#  trc_cfg.write(txt)
#  flush_and_close( trc_cfg )
#  
#  #####################################################################
#  # Async. launch of trace session using FBSVCMGR action_trace_start:
#  
#  trc_log=open( os.path.join(context['temp_directory'],'tmp_trace_5991.log'), 'w')
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  p_svcmgr = Popen( [ context['fbsvcmgr_path'], "localhost:service_mgr",
#                      "action_trace_start",
#                      "trc_cfg", trc_cfg.name
#                    ],
#                    stdout=trc_log, 
#                    stderr=subprocess.STDOUT
#                  )
#  
#  # 08.01.2020. This delay is mandatory, otherwise file with trace session info can remain (sometimes)
#  # empty when we will read it at the next step:
#  time.sleep(1)
#  
#  # Determine active trace session ID (for further stop):
#  ########################
#  trc_lst=open( os.path.join(context['temp_directory'],'tmp_trace_5991.lst'), 'w')
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_trace_list"],
#                   stdout=trc_lst, stderr=subprocess.STDOUT
#                 )
#  flush_and_close( trc_lst )
#  
#  # Session ID: 5 
#  #   user:   
#  #   date:  2015-08-27 15:24:14 
#  #   flags: active, trace 
#  
#  sid_pattern = re.compile('Session\\s+ID[:]{0,1}\\s+\\d+', re.IGNORECASE)
#  
#  trc_ssn=0
#  with open( trc_lst.name,'r') as f:
#      for line in f:
#          if sid_pattern.search( line ) and len( line.split() ) == 3:
#              trc_ssn = line.split()[2]
#              break
#  
#  # Result: `trc_ssn` is ID of active trace session. 
#  # We have to terminate trace session that is running on server BEFORE we termitane process `p_svcmgr`
#  
#  if trc_ssn==0:
#      print("Error parsing trace session ID.")
#      flush_and_close( trc_log )
#  
#  else:
#  
#      ###########   W O R K    W I T H    D A T A B A S E    ########
#  
#      print( 'Trying to create: "localhost:%s"' % fdb_file.replace("'","''") )
#      con = fdb.create_database( dsn = "localhost:%s" % fdb_file.replace("'","''") )
#      print( 'Database created OK.' )
#      cur = con.cursor()
#      cur.execute( "select 'Database name contains single quote.' as result from mon$database where lower(mon$database_name) similar to '%[\\/](tmp_5991.o''clock).fdb'")
#      for r in cur:
#          print(r[0])
#  
#      cur.close()
#      con.drop_database()
#      print( 'Database dropped OK.')
#      #####################################################################
#  
#      # ::: NB ::: Here we have to be idle at least 2s (two seconds) otherwise trace log will 
#      # not contain some or all of messages about create DB, start Tx, ES, Tx and drop DB.
#      # See also discussion with hvlad, 08.01.2020 15:16
#      # (subj: "action_trace_stop does not flush trace log (fully or partially)")
#      time.sleep(2)
#  
#      # Stop trace session:
#      #####################
#  
#      trc_lst=open(trc_lst.name, "a")
#      trc_lst.seek(0,2)
#  
#      subprocess.call( [ context['fbsvcmgr_path'], "localhost:service_mgr",
#                         "action_trace_stop",
#                         "trc_id",trc_ssn
#                       ],
#                       stdout=trc_lst, 
#                       stderr=subprocess.STDOUT
#                     )
#      flush_and_close( trc_lst )
#  
#      # 23.02.2021. DELAY FOR AT LEAST 1 SECOND REQUIRED HERE!
#      # Otherwise trace log can remain empty.
#      time.sleep(1)
#  
#      p_svcmgr.terminate()
#      flush_and_close( trc_log )
#  
#      allowed_patterns = {
#           '1. TRACE_START'    : re.compile('Trace\\s+session\\s+ID\\s+\\d+\\s+started\\.*', re.IGNORECASE)
#          ,'2. DB_CREATION'    : re.compile('[.*]*CREATE_DATABASE\\.*', re.IGNORECASE)
#          ,'3. TX_START'       : re.compile('[.*]*START_TRANSACTION\\.*', re.IGNORECASE)
#          ,'4. STATEMENT_DONE' : re.compile('[.*]*EXECUTE_STATEMENT_FINISH\\.*', re.IGNORECASE)
#          ,'5. TX_FINISH'      : re.compile('[.*]*ROLLBACK_TRANSACTION\\.*', re.IGNORECASE)
#          ,'6. DB_REMOVAL'     : re.compile('[.*]*DROP_DATABASE\\.*', re.IGNORECASE)
#      }
#  
#      found_patterns={}
#  
#      with open( trc_log.name,'r') as f:
#          for line in f:
#              if line.rstrip().split():
#                  for k,v in allowed_patterns.items():
#                      if v.search(line):
#                          found_patterns[k] = 'FOUND'
#  
#      for k,v in sorted( found_patterns.items() ):
#          print( 'Pattern', k, ':', v)
#  
#      if len( found_patterns ) < len( allowed_patterns ):
#          print('==== INCOMPLETE TRACE LOG: ====')
#          with open( trc_log.name,'r') as f:
#              for line in f:
#                  if line.rstrip().split():
#                      print('  ' + line)
#          print('=' * 31)
#  
#  #< cond "if trc_ssn>0"
#  
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (trc_lst, trc_cfg, trc_log) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Trying to create: "localhost:C:/FBTESTING/qa/fbt-repo/tmp/tmp_5991.o''clock.fdb"
    Database created OK.
    Database name contains single quote.
    Database dropped OK.
    Pattern 1. TRACE_START : FOUND
    Pattern 2. DB_CREATION : FOUND
    Pattern 3. TX_START : FOUND
    Pattern 4. STATEMENT_DONE : FOUND
    Pattern 5. TX_FINISH : FOUND
    Pattern 6. DB_REMOVAL : FOUND
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


