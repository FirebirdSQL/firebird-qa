#coding:utf-8
#
# id:           bugs.core_5793
# title:        Error returned from DbCryptPlugin::setKey() is not shown
# decription:   
#               
#                   Test database that is created by fbtest framework will be encrypted here using IBSurgeon Demo Encryption package
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
#                   Firstly we try to encrypt DB with existing key and decrypt it aftee this - just to ensure that this mechanism works fine.
#                   Then we use statement 'alter database encrypt ...' with NON existing key and check parts of exception that will raise.
#                   From these three parts (multi-string, int and bigint numbers) we check that 1st contains phrase about missed crypt key.
#                   ::: NOTE :::: 
#                   Text of messages differ in 3.0.5 vs 4.0.0:
#                       3.0.5: - Missing correct crypt key
#                       4.0.0: - Missing database encryption key for your attachment
#                   - so we use regexp tool for check pattern matching. 
#                   Because of different text related to missing plugin, this part is replaced with phrase: 
#                   <MESSAGE ABOUT MISSED ENCRYPTION KEY HERE> -- both for 3.0.x  and 4.0.x.
#               
#                   Confirmed difference in error message (text decription, w/o sqlcode and gdscode):
#                   1) 3.0.3.32900
#                   =====
#                       Error while executing SQL statement:
#                       - SQLCODE: -607
#                       - unsuccessful metadata update
#                       - ALTER DATABASE failed
#                       - Missing correct crypt key
#                   =====
#               
#                   2) 3.0.5.33139 - two lines were added:
#                   ====
#                       - Plugin KeyHolder:
#                       - Unknown key name FOO - key can't be found in KeyHolder.conf
#                   ====
#               
#                   Checked on:
#                       4.0.0.1524: OK, 4.674s.
#                       3.0.5.33139: OK, 3.666s.
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
#                   === NOTE-3 ===
#                   firebird.conf must contain following line:
#                       KeyHolderPlugin = KeyHolder
#               
#                
# tracker_id:   CORE-5793
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import re
#  import time
#  
#  # Messages differ:
#  # 3.0.5: - Missing correct crypt key
#  # 4.0.0: - Missing database encryption key for your attachment
#  # --> we can use regexp to parse exception text and try to find some common words for these messages:
#  missed_key_ptn=re.compile('.*missing\\s+.*(crypt key|encryption key).*', re.IGNORECASE)
#  
#  print('1.1. Trying to encrypt with existing key.')
#  db_conn.execute_immediate('alter database encrypt with dbcrypt key red')
#  db_conn.commit()
#  time.sleep(1)
#  print('1.2. Delay completed, DB now must be encrypted.')
#  
#  print('2.1. Trying to decrypt.')
#  db_conn.execute_immediate('alter database decrypt')
#  db_conn.commit()
#  time.sleep(2)
#  print('2.2. Delay completed, DB now must be decrypted.')
#  
#  print('3.1. Trying to encrypt with non-existing key')
#  try:
#      db_conn.execute_immediate('alter database encrypt with dbcrypt key foo')
#      db_conn.commit()
#      time.sleep(1)
#      print('3.2 ??? ERROR ??? Encrypted with key "foo" ?!')
#  except Exception as e:
#      for x in e.args:
#          if isinstance( x, str):
#              for r in x.split('\\n'):
#                  if missed_key_ptn.search( r ):
#                      print('<MESSAGE ABOUT MISSED ENCRYPTION KEY HERE>')
#                  else:
#                      print( r )
#          else:
#              print(x)
#  
#  finally:
#      db_conn.close()
#  '''
#      1.1. Trying to encrypt with existing key.
#      1.2. Delay completed, DB now must be encrypted.
#      2.1. Trying to decrypt.
#      2.2. Delay completed, DB now must be decrypted.
#      3.1. Trying to encrypt with non-existing key
#      Error while executing SQL statement:
#      - SQLCODE: -607
#      - unsuccessful metadata update
#      - ALTER DATABASE failed
#      - Missing correct crypt key
#      - Plugin KeyHolder:
#      - Unknown key name FOO - key can't be found in KeyHolder.conf
#      -607
#      335544351
#  
#  '''
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1.1. Trying to encrypt with existing key.
    1.2. Delay completed, DB now must be encrypted.
    2.1. Trying to decrypt.
    2.2. Delay completed, DB now must be decrypted.
    3.1. Trying to encrypt with non-existing key
    Error while executing SQL statement:
    - SQLCODE: -607
    - unsuccessful metadata update
    - ALTER DATABASE failed
    <MESSAGE ABOUT MISSED ENCRYPTION KEY HERE>
    - Plugin KeyHolder:
    - Unknown key name FOO - key can't be found in KeyHolder.conf
    -607
    335544351
  """

@pytest.mark.version('>=3.0.4')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_5793_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


