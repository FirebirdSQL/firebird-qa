#coding:utf-8
#
# id:           bugs.core_6947
# title:        Query to mon$ tables does not return data when the encryption/decryption thread is running
# decription:   
#                   Test creates table with wide indexed column and add some data to it.
#                   Volume of data must be big enough enough so that the encryption process does not have time to end in 1 second.
#               
#                   Then ALTER DATABASE ENCRYPT ... is called and we allow encryption process to work for 1 second.
#                   After this we query MON$DATABASE and check that MON$CRYPT_STATE column has value = 3 ('is encrypting').
#                   Before fix this value always was 1, i.e. 'fully encrypted' - because control returned to 'main' code only
#                   after encryption process was completed.
#               
#                   Note: name for encryption plugin differs on Windows vs Linux:
#                      PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else '"fbSampleDbCrypt"'
#               
#                   Confirmed bug on 5.0.0.219 (Windows), 5.0.0.236 (Linux).
#                   Checked on 5.0.0.240 (Windows; SS/Cs), 5.0.0.241 (Linux; SS/CS).
#                
# tracker_id:   CORE-6947
# min_versions: ['5.0.0']
# versions:     5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  import re
#  import fdb
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  engine = db_conn.engine_version
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
#            print('type(f_names_list[i])=',type(f_names_list[i]))
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_6947.fdb'
#  
#  cleanup( (tmpfdb,) )
#  
#  con = fdb.create_database( dsn = tmpfdb, page_size = 4096 )
#  con.close()
#  runProgram('gfix',[tmpfdb,'-w','async'])
#  
#  con = fdb.connect( dsn = tmpfdb )
#  con.execute_immediate( 'create table test(s varchar(1000))' )
#  con.commit()
#  
#  sql_init='''
#  execute block as
#      declare n int = 100000;
#  begin
#      while (n>0) do
#      begin
#          insert into test(s) values( lpad('', 1000, uuid_to_char(gen_uuid())) );
#          n = n-1;
#      end
#  end
#  '''
#  con.execute_immediate(sql_init)
#  con.commit()
#  con.execute_immediate( 'create index test_s on test(s)' )
#  con.commit()
#  
#  con.close()
#  runProgram('gfix',[tmpfdb,'-w','sync'])
#  
#  #-----------------------------------------------------
#  
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else ( '"fbSampleDbCrypt"' if engine >= 4.0 else '"DbCrypt_example"')
#  
#  customTPB = ( [ fdb.isc_tpb_read_committed, fdb.isc_tpb_rec_version, fdb.isc_tpb_nowait ] )
#  con = fdb.connect( dsn = tmpfdb, isolation_level = customTPB )
#  cur = con.cursor()
#  
#  ##############################################
#  # WARNING! Do NOT use 'connection_obj.execute_immediate()' for ALTER DATABASE ENCRYPT... command!
#  # There is bug in FB driver which leads this command to fail with 'token unknown' message
#  # The reason is that execute_immediate() silently set client dialect = 0 and any encryption statement
#  # can not be used for such value of client dialect.
#  # One need to to use only cursor_obj.execute() for encryption!
#  # See letter from Pavel Cisar, 20.01.20 10:36
#  ##############################################
#  cur.execute('alter database encrypt with %(PLUGIN_NAME)s key Red' % locals())
#  con.commit()
#  
#  # Let encryption process start its job:
#  time.sleep(1)
#  
#  # Before this ticket was fixed query to mon$ tables did not return data until encryption fully completed.
#  # This means that we could see only mon$crypt_state = 1 ("fully encrypted").
#  # After fix, we must see that DB is currently encrypting:
#  #
#  crypt_state_map = {0: 'not encrypted', 1: 'fully encrypted', 2: 'is decrypting', 3: 'is encrypting'}
#  cur.execute('select m.mon$crypt_state from mon$database m')
#  for r in cur:
#      db_crypt_state = crypt_state_map.get( r[0], 'UNKNOWN' )
#  
#  cur.close()
#  con.close()
#  
#  print('DB encryption state: %s.' % db_crypt_state)
#  
#  #---------------------------- shutdown temp DB --------------------
#  
#  f_dbshut_log = open( os.path.join(context['temp_directory'],'tmp_dbshut_6947.log'), 'w')
#  subprocess.call( [ context['gfix_path'], 'localhost:'+tmpfdb, "-shut", "full", "-force", "0" ],
#                   stdout = f_dbshut_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_dbshut_log )
#  
#  with open( f_dbshut_log.name,'r') as f:
#      for line in f:
#          print("Unexpected error on SHUTDOWN temp database: "+line)
#  
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( ( f_dbshut_log,tmpfdb )  )
#  
#---
act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    DB encryption state: is encrypting.
"""

@pytest.mark.version('>=5.0')
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


