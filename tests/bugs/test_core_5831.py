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
#                   Anyone who wants to run this test on his own machine must
#                   1) download https://ib-aid.com/download/crypt/CryptTest.zip AND 
#                   2) PURCHASE LICENSE and get from IBSurgeon file plugins\\dbcrypt.conf with apropriate expiration date and other info.
#                   
#                   ################################################ ! ! !    N O T E    ! ! ! ##############################################
#                   FF tests storage (aka "fbt-repo") does not (and will not) contain any license file for IBSurgeon Demo Encryption package!
#                   #########################################################################################################################
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
#                   === NOTE-1 ===
#                   In case of "Crypt plugin DBCRYPT failed to load/607/335544351" check that all 
#                   needed files from IBSurgeon Demo Encryption package exist in %FB_HOME% and %FB_HOME%\\plugins
#                   %FB_HOME%:
#                       283136 fbcrypt.dll
#                      2905600 libcrypto-1_1-x64.dll
#                       481792 libssl-1_1-x64.dll
#               
#                   %FB_HOME%\\plugins:
#                       297984 dbcrypt.dll
#                       306176 keyholder.dll
#                          108 DbCrypt.conf
#                          856 keyholder.conf
#                   
#                   === NOTE-2 ===
#                   Version of DbCrypt.dll of october-2018 must be replaced because it has hard-coded 
#                   date of expiration rather than reading it from DbCrypt.conf !!
#               
#                
# tracker_id:   CORE-5831
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = [('CRYPT CHECKSUM.*', 'CRYPT CHECKSUM'), ('KEY HASH.*', 'KEY HASH')]

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
#  db_conn.close()
#  
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_5831.fdb'
#  
#  if os.path.isfile( tmpfdb ):
#      os.remove( tmpfdb )
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb )
#  con.close()
#  con=fdb.connect( dsn = 'localhost:'+tmpfdb )
#  cur = con.cursor()
#  cur.execute('alter database encrypt with dbcrypt key Red')
#  con.commit()
#  
#  time.sleep(1)
#  #          ^
#  #          +-------- !! ALLOW BACKGROUND ENCRYPTION PROCESS TO COMPLETE ITS JOB !!
#  
#  con.close()
#  
#  f_gstat_log = open( os.path.join(context['temp_directory'],'tmp_shut_5831.log'), 'w')
#  f_gstat_err = open( os.path.join(context['temp_directory'],'tmp_shut_5831.err'), 'w')
#  
#  subprocess.call( [ "gstat", "-h", tmpfdb],
#                   stdout = f_gstat_log,
#                   stderr = f_gstat_err
#                 )
#  
#  subprocess.call( [ "gfix", 'localhost:'+tmpfdb, "-shut", "full", "-force", "0" ],
#                   stdout = f_gstat_log,
#                   stderr = f_gstat_err
#                 )
#  
#  f_gstat_log.close()
#  f_gstat_err.close()
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
#  f_list=(f_gstat_log, f_gstat_err)
#  for i in range(len(f_list)):
#     if os.path.isfile(f_list[i].name):
#         os.remove(f_list[i].name)
#  
#  if os.path.isfile( tmpfdb ):
#      os.remove( tmpfdb )
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
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_5831_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


