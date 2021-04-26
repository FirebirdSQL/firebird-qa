#coding:utf-8
#
# id:           bugs.core_5673
# title:        Unique constraint not working in encrypted database on first command
# decription:   
#               
#                   We create new database ('tmp_core_5673.fdb') and try to encrypt it using IBSurgeon Demo Encryption package
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
#                   We create table with UNIQUE constraint, add some data to it and try to encrypt database using 'alter database encrypt with <plugin_name> ...'
#                   command (where <plugin_name> = dbcrypt - name of .dll in FB_HOME\\plugins\\  folder that implements encryption).
#                   Then we allow engine to complete this job - take delay about 1..2 seconds BEFORE detach from database.
#               
#                   After this we make TWO attempts to insert duplicates and catch exceptions for each of them and print exception details.
#                   Expected result: TWO exception must occur here.
#                   
#                   ::: NB ::::
#                   Could not check reproducing of bug on FB 3.0.2 because there is no encryption plugin for this (too old) version.
#                   Decided only to ensure that exception will be catched on recent FB version for each attempt to insert duplicate.
#                   Checked on:
#                        4.0.0.1524: OK, 4.056s ;  4.0.0.1421: OK, 6.160s.
#                       3.0.5.33139: OK, 2.895s ; 3.0.5.33118: OK, 2.837s.
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
# tracker_id:   CORE-5673
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
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
#  
#  db_conn.close()
#  
#  #---------- aux func for cleanup: ---------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  
#  #------------------------------------------
#  
#  
#  con = fdb.connect( dsn = dsn )
#  con.execute_immediate( 'recreate table test(x int, constraint test_x_unq unique(x))' )
#  con.commit()
#  
#  cur = con.cursor()
#  cur.execute( 'insert into test(x) select row_number()over() from rdb$types rows 10' )
#  con.commit()
#  
#  cur.execute('alter database encrypt with dbcrypt key Red')
#  con.commit()
#  
#  time.sleep(2)
#  #          ^
#  #          +-------- !! ALLOW BACKGROUND ENCRYPTION PROCESS TO COMPLETE ITS JOB !!
#  
#  try:
#      cur.execute( 'insert into test(x) values(1)' )
#  except Exception as e:
#      for x in e.args:
#          print( x  )
#  
#  try:
#      cur.execute( 'insert into test(x) values(2)' )
#  except Exception as e:
#      for x in e.args:
#          #print( x.replace(chr(92),"/") if type(x)=='str' else x  )
#          print( x  )
#  
#  
#  cur.close()
#  con.close()
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Error while executing SQL statement:
    - SQLCODE: -803
    - violation of PRIMARY or UNIQUE KEY constraint "TEST_X_UNQ" on table "TEST"
    - Problematic key value is ("X" = 1)
    -803
    335544665

    Error while executing SQL statement:
    - SQLCODE: -803
    - violation of PRIMARY or UNIQUE KEY constraint "TEST_X_UNQ" on table "TEST"
    - Problematic key value is ("X" = 2)
    -803
    335544665
  """

@pytest.mark.version('>=3.0.3')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_5673_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


