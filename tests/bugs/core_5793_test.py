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
#                   First, we try to encrypt DB with existing key and decrypt it aftee this - just to ensure that this mechanism works fine.
#                   Then we use statement 'alter database encrypt ...' with NON existing key and check parts of exception that will raise.
#                   From these three parts (multi-string, int and bigint numbers) we check that 1st contains phrase about missed crypt key.
#                   ::: NOTE :::: 
#                   Text of messages differ in 3.0.5 vs 4.0.0:
#                       3.0.5: - Missing correct crypt key
#                       4.0.0: - Missing database encryption key for your attachment
#                   - so we use regexp tool for check pattern matching. 
#                   Because of different text related to missing plugin, this part is replaced with phrase: 
#                   <FOUND PATTERN-1 ABOUT MISSED ENCRYPTION KEY> -- both for 3.0.x  and 4.0.x.
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
#                   15.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 4.0.0.2416
#                     Linux:   4.0.0.2416
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
#  engine = db_conn.engine_version
#  
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
#  cur = db_conn.cursor()
#  
#  print('1.1. Trying to encrypt with existing key.')
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
#  db_conn.commit()
#  
#  time.sleep(2)
#  
#  print('1.2. Delay completed, DB now must be encrypted.')
#  
#  print('2.1. Trying to decrypt.')
#  cur.execute('alter database decrypt')
#  db_conn.commit()
#  time.sleep(2)
#  print('2.2. Delay completed, DB now must be decrypted.')
#  
#  print('3.1. Trying to encrypt with non-existing key')
#  try:
#      cur.execute('alter database encrypt with %(PLUGIN_NAME)s key no_such_key_foo' % locals())
#      db_conn.commit()
#      time.sleep(1)
#      print('3.2 ### ERROR ### Encrypted with non-existing key ?')
#  except Exception as e:
#      # Messages about incorrect key differ depending of FB major version:
#      #     3.0.5: - Missing correct crypt key
#      #     4.0.0: - Missing database encryption key for your attachment
#      #     --> we can use regexp to parse exception text and try to find some common words for these messages:
#      # Messages about missing this key in the keyholder differ depending on OS:
#      # Windows:
#      #    - Plugin KeyHolder:
#      #    Unknown key name NO_SUCH_KEY_FOO - key can't be found in KeyHolder.conf
#      # Linux:
#      #    - Plugin CryptKeyHolder_example:
#      # Crypt key NO_SUCH_KEY_FOO not set
#      
#      missed_key_ptn1 = re.compile('.*missing\\s+.*(crypt key|encryption key).*', re.IGNORECASE)
#      missed_key_ptn2 = ''
#      if os.name == 'nt':
#          missed_key_ptn2 = re.compile(".*Unknown\\s+key\\s+name.*key\\s+can't\\s+be\\s+found.*", re.IGNORECASE)
#      else:
#          missed_key_ptn2 = re.compile(".*Crypt\\s+key\\s+.*\\s+not\\s+set", re.IGNORECASE)
#  
#      for x in e.args:
#          if isinstance( x, str):
#              for r in x.split('\\n'):
#                  if missed_key_ptn1.search( r ):
#                      print('<FOUND PATTERN-1 ABOUT MISSED ENCRYPTION KEY>')
#                  elif missed_key_ptn2.search( r ):
#                      print('<FOUND PATTERN-2 ABOUT MISSED ENCRYPTION KEY>')
#                  elif r.strip().lower().startswith('- plugin'):
#                      pass
#                  else:
#                      print( r )
#          else:
#              print(x)
#  finally:
#      cur.close()
#      db_conn.close()
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
    <FOUND PATTERN-1 ABOUT MISSED ENCRYPTION KEY>
    <FOUND PATTERN-2 ABOUT MISSED ENCRYPTION KEY>    
    -607
    335544351
  """

@pytest.mark.version('>=3.0.4')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


