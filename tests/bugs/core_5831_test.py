#coding:utf-8
#
# id:           bugs.core_5831
# title:        Not user friendly output of gstat at encrypted database
# decription:   
#                   We create new database ('tmp_core_5831.fdb') and try to encrypt it usng IBSurgeon Demo Encryption package
#                   ( https://ib-aid.com/download-demo-firebird-encryption-plugin/ ; https://ib-aid.com/download/crypt/CryptTest.zip )
#                   License file plugins\\dbcrypt.conf with unlimited expiration was provided by IBSurgeon to Firebird Foundation (FF).
#                   This file was preliminary stored in FF Test machine.
#                   Test assumes that this file and all neccessary libraries already were stored into FB_HOME and %FB_HOME%\\plugins.
#               
#                   After test database will be created, we try to encrypt it using 'alter database encrypt with <plugin_name> ...' command
#                   (where <plugin_name> = dbcrypt - name of .dll in FB_HOME\\plugins\\ folder that implements encryption).
#                   Then we allow engine to complete this job - take delay about 1..2 seconds BEFORE detach from database.
#               
#                   After this we detach from DB, run 'gstat -h' and filter its attributes and messages from 'Variable header' section.
#                   In the output of gstat we check that its 'tail' will look like this:
#                   ===
#                       Attributes	force write, encrypted, plugin DBCRYPT
#                       Crypt checksum:	MUB2NTJqchh9RshmP6xFAiIc2iI=
#                       Key hash: ask88tfWbinvC6b1JvS9Mfuh47c=
#                       Encryption key name: RED
#                   ===
#                   (concrete values for checksum and hash will be ignored - see 'substitutions' section).
#               
#                   Finally, we change this temp DB statee to full shutdown in order to have 100% ability to drop this file.
#               
#                   Checked on:
#                       40sS, build 4.0.0.1487: OK, 3.347s.
#                       40Cs, build 4.0.0.1487: OK, 3.506s.
#                       30sS, build 3.0.5.33120: OK, 2.697s.
#                       30Cs, build 3.0.5.33120: OK, 3.054s.
#               
#                   15.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 4.0.0.2416
#                     Linux:   4.0.0.2416
#                
# tracker_id:   CORE-5831
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = [('ATTRIBUTES FORCE WRITE, ENCRYPTED, PLUGIN.*', 'ATTRIBUTES FORCE WRITE, ENCRYPTED'), ('CRYPT CHECKSUM.*', 'CRYPT CHECKSUM'), ('KEY HASH.*', 'KEY HASH')]

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
#  
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_5831.fdb'
#  
#  cleanup( (tmpfdb,) )
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb )
#  cur = con.cursor()
#  
#  # 14.04.2021.
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else ( '"fbSampleDbCrypt"' if engine >= 4.0 else '"DbCrypt_example"')
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
#  
#  con.commit()
#  
#  time.sleep(2)
#  #          ^
#  #          +-------- !! ALLOW BACKGROUND ENCRYPTION PROCESS TO COMPLETE ITS JOB !!
#  # DO NOT set this delay less than 2 seconds otherwise "crypt process" will be in the output!
#  
#  con.close()
#  
#  f_gstat_log = open( os.path.join(context['temp_directory'],'tmp_shut_5831.log'), 'w')
#  f_gstat_err = open( os.path.join(context['temp_directory'],'tmp_shut_5831.err'), 'w')
#  
#  subprocess.call( [ context['gstat_path'], "-h", tmpfdb],
#                   stdout = f_gstat_log,
#                   stderr = f_gstat_err
#                 )
#  
#  subprocess.call( [ context['gfix_path'], 'localhost:'+tmpfdb, "-shut", "full", "-force", "0" ],
#                   stdout = f_gstat_log,
#                   stderr = f_gstat_err
#                 )
#  
#  flush_and_close( f_gstat_log )
#  flush_and_close( f_gstat_err )
#  
#  allowed_patterns = (
#        re.compile( '\\s*Attributes\\.*', re.IGNORECASE)
#       ,re.compile('crypt\\s+checksum:\\s+\\S+', re.IGNORECASE)
#       ,re.compile('key\\s+hash:\\s+\\S+', re.IGNORECASE)
#       ,re.compile('encryption\\s+key\\s+name:\\s+\\S+', re.IGNORECASE)
#  )
#  
#  with open( f_gstat_log.name,'r') as f:
#      for line in f:
#          match2some = filter( None, [ p.search(line) for p in allowed_patterns ] )
#          if match2some:
#              print( (' '.join( line.split()).upper() ) )
#  
#  with open( f_gstat_err.name,'r') as f:
#      for line in f:
#          print("Unexpected STDERR: "+line)
#  
#  
#  # cleanuo:
#  time.sleep(1)
#  cleanup( (f_gstat_log, f_gstat_err, tmpfdb) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ATTRIBUTES FORCE WRITE, ENCRYPTED, PLUGIN DBCRYPT
    CRYPT CHECKSUM: MUB2NTJQCHH9RSHMP6XFAIIC2II=
    KEY HASH: ASK88TFWBINVC6B1JVS9MFUH47C=
    ENCRYPTION KEY NAME: RED
  """

@pytest.mark.version('>=3.0.4')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


