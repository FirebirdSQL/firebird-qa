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
#                   15.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 4.0.0.2416
#                     Linux:   4.0.0.2416
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
#  engine = db_conn.engine_version
#  db_conn.close()
#  
#  # 14.04.2021.
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else ( '"fbSampleDbCrypt"' if engine >= 4.0 else '"DbCrypt_example"')
#  KHOLDER_NAME = 'KeyHolder' if os.name == 'nt' else "fbSampleKeyHolder"
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
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


