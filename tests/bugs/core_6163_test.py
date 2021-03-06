#coding:utf-8
#
# id:           bugs.core_6163
# title:        Generator pages are not encrypted
# decription:   
#                   Database in this test is encrypted using IBSurgeon Demo Encryption package
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
#                   Several sequences are created in this test. 
#                   Then we obtain generator page ID and page size by querying RDB$PAGES and MON$DATABASE tables.
#                   After this, we check that values of sequences *PRESENT* in NON-encrypted database by opening DB file in 'rb' mode
#                   and reading content of its generator page.
#                   Further, we encrypt database and wait for 1 second in order to give engine complete this job.
#                   Finally, we read generator page again. NO any value of secuences must be found at this point.
#               
#                   Encryprion is performed by 'alter database encrypt with <plugin_name> key ...' statement,
#                   where <plugin_name> = dbcrypt - is the name of .dll in FB_HOME\\plugins\\  folder that implements encryption.
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
#                   Confirmed non-encrypted content of generators page on: 4.0.0.1627; 3.0.5.33178.
#                   Checked on: 4.0.0.1633: OK, 2.260s; 3.0.5.33180: OK, 1.718s.
#               
#                   :::::::::::::::::::::::::::::::::::::::: NB ::::::::::::::::::::::::::::::::::::
#                   18.08.2020. FB 4.x has incompatible behaviour with all previous versions since build 4.0.0.2131 (06-aug-2020):
#                   statement 'alter sequence <seq_name> restart with 0' changes rdb$generators.rdb$initial_value to -1 thus next call
#                   gen_id(<seq_name>,1) will return 0 (ZERO!) rather than 1. 
#                   See also CORE-6084 and its fix: https://github.com/FirebirdSQL/firebird/commit/23dc0c6297825b2e9006f4d5a2c488702091033d
#                   ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#                   This is considered as *expected* and is noted in doc/README.incompatibilities.3to4.txt
#               
#                   Because of this, it was decided to make separate section for check results of FB 4.x
#                   Checked on 4.0.0.2164, 3.0.7.33356
#               
#                   28.02.2021
#                   For unknown reason 3.x and 4.x Classic hangs during run this test, both on Linux and (unexpectedly) Windows.
#                   Fortunately, simple solution was found.
#                   FB hangs only when encryption is done in ISQL but we wait for its finish within 'main' (Python) code (rather than in ISQL).
#                   If we force ISQL *itself*  wait for several seconds than all fine.
#                   So, the only way to avoid hang (at least nowadays, 01-mar-2021) is to make encryption *and* waiting for its finish
#                   within ONE attachment to the database that is created by ISQL.
#                   Because of this, 'init_script' contains special table and procedure for making pauses: 'tets' and 'sp_delay'.
#                   Procedure 'sp_delay' must be called within Tx which was declared as SET TRANSACTION LOCK TIMEOU <N> where <N> =  1...3.
#               
#                   Checked on: 4.0.0.2372 SS/CS; 3.0.8.33420 SS/CS.
#               
#                
# tracker_id:   CORE-6163
# min_versions: ['3.0.5']
# versions:     3.0.5, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = [('^((?!(FOUND.|Database\\s+encrypted)).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """
    recreate table test(x bigint unique);
    set term ^;
    create or alter procedure sp_delay as
        declare r bigint;
    begin
        r = rand() * 9223372036854775807;
        insert into test(x) values(:r);
        begin
            -- #########################################################
            -- #######################  D E L A Y  #####################
            -- #########################################################
            in autonomous transaction do
            insert into test(x) values(:r); -- this will cause delay because of duplicate in index
        when any do 
            begin
                -- nop --
            end
        end
    end
    ^
    set term ;^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import binascii
#  import time
#  #import shutil
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  this_fdb = db_conn.database_name
#  # ::: NB ::: DO NOT close db_conn now! We can close it only after encryption will finish!
#  
#  db_conn.execute_immediate('create sequence gen_ba0bab start with 12192683')
#  db_conn.execute_immediate('create sequence gen_badf00d start with 195948557')
#  db_conn.execute_immediate('create sequence gen_caca0  start with 830624')
#  db_conn.execute_immediate('create sequence gen_c0ffee start with 12648430')
#  db_conn.execute_immediate('create sequence gen_dec0de start with 14598366')
#  db_conn.execute_immediate('create sequence gen_decade start with 14600926')
#  db_conn.execute_immediate('create sequence gen_7FFFFFFF start with 2147483647')
#  db_conn.commit()
#  
#  ######################################################################################
#  
#  def check_page_for_readable_values(dbname, gen_page_number, pg_size, check_sequence_values):
#  
#      global binascii
#  
#      db_handle = open( dbname, "rb")
#      db_handle.seek( gen_page_number * pg_size )
#      page_content = db_handle.read( pg_size )
#      # read_binary_content( db_handle, gen_page_number * pg_size, pg_size )
#      db_handle.close()
#      page_as_hex=binascii.hexlify( page_content )
#  
#      # Iterate for each sequence value:
#      for n in check_sequence_values:
#  
#          # Get HEX representation of digital value.
#          # NOTE: format( 830624, 'x') is 'caca0' contains five (odd number!) characters.
#          hex_string = format(abs(n),'x')
#  
#          # Here we 'pad' hex representation to EVEN number of digits in it,
#          # otherwise binascii.hexlify fails with "Odd-length string error":
#          hex_string = ''.join( ('0' * ( len(hex_string)%2 ), hex_string ) )
#  
#          # ::: NOTE :::
#          # Generator value is stored in REVERSED bytes order.
#          # dec 830624 --> hex 0x0caca0 --> 0c|ac|a0 --> stored in page as three bytes: {a0; ac; 0c}
#  
#          # Decode string that is stored in variable 'hex_string' to HEX number,
#          # REVERSE its bytes and convert it to string again for further search
#          # in page content:
#          n_as_reversed_hex = binascii.hexlify( hex_string.decode('hex')[::-1] )
#  
#          print(n, n_as_reversed_hex, 'FOUND.' if n_as_reversed_hex in page_as_hex else 'NOT FOUND.' )
#          # print(n, n_as_reversed_hex, 'UNEXPECTEDLY FOUND AT POS. ' + '{:5d}'.format( page_as_hex.index(n_as_reversed_hex) ) if n_as_reversed_hex in page_as_hex else 'Not found (expected).' )
#  
#  ######################################################################################
#  
#  
#  cur=db_conn.cursor()
#  get_current_seq_values='''
#      execute block returns( gen_curr bigint) as
#          declare gen_name rdb$generator_name;
#      begin
#          for
#              select rdb$generator_name from rdb$generators where rdb$system_flag is distinct from 1 order by rdb$generator_id
#              into gen_name
#          do begin
#              execute statement 'execute block returns(g bigint) as begin g = gen_id('|| gen_name ||', 0); suspend;  end' into gen_curr;
#              suspend;
#          end
#      end
#  '''
#  
#  # Obtain current values of user generators:
#  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  cur.execute(get_current_seq_values)
#  check_sequence_values=[]
#  for r in cur:
#      check_sequence_values += r[0],
#  
#  
#  # Obtain page size and number of generators page:
#  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  cur.execute('select m.mon$page_size,min(rdb$page_number) from mon$database m cross join rdb$pages p where p.rdb$page_type = 9 group by 1')
#  pg_size, gen_page_number = -1,-1
#  for r in cur:
#      pg_size=r[0]
#      gen_page_number=r[1]
#      # print(r[0],r[1])
#  cur.close()
#  db_conn.close()
#  
#  # Read gen page, convert it to hex and check whether generator values can be found there or no:
#  # Expected result: YES for all values because DB not encrypted now.
#  # ~~~~~~~~~~~~~~~
#  check_page_for_readable_values(this_fdb, gen_page_number, pg_size, check_sequence_values)
#  
#  # 27.02.2021.
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  #      later it can be replaced with built-in plugin 'fbSampleDbCrypt'
#  #      but currently it is included only in FB 4.x builds (not in FB 3.x).
#  #      Discussed tih Dimitr, Alex, Vlad, letters since: 08-feb-2021 00:22
#  #      "Windows-distributive FB 3.x: it is desired to see sub-folder 'examples\\prebuild' with files for encryption, like it is in FB 4.x
#  #      *** DEFERRED ***
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else ( '"DbCrypt_example"' if db_conn.engine_version < 4 else '"fbSampleDbCrypt"' )
#  
#  sql_cmd='''
#      -- ################################################
#      -- ###    e n c r y p t      d a t a b a s e    ###
#      -- ################################################
#      alter database encrypt with %(PLUGIN_NAME)s key Red;
#      commit;
#  
#      
#      -- 01.03.2021: we have to wait for several seconds
#      -- until encryption will be finished. But we must do
#      -- this delay within the same attachment as those that
#      -- launched encryption process.
#      -- The reason of that weird effect currently is unknown.
#      -- Here we make pause using 'set transaction lock timeout':
#  
#      set transaction lock timeout 2; -- THIS LOCK TIMEOUT SERVES ONLY FOR DELAY
#      execute procedure sp_delay;
#      rollback;
#      show database;
#      quit;
#  ''' % locals()
#  
#  runProgram('isql', [ dsn ], sql_cmd)
#  
#  # Read again gen page, convert it to hex and check whether generator values can be found there or no.
#  # Expected result: NOT for all values because DB was encrypted.
#  # ~~~~~~~~~~~~~~~~
#  check_page_for_readable_values(this_fdb, gen_page_number, pg_size, check_sequence_values)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
12192683   ab0bba   FOUND.
195948557  0df0ad0b FOUND.
830624     a0ac0c   FOUND.
12648430   eeffc0   FOUND.
14598366   dec0de   FOUND.
14600926   decade   FOUND.
2147483647 ffffff7f FOUND.

Database encrypted

12192683   ab0bba   NOT FOUND.
195948557  0df0ad0b NOT FOUND.
830624     a0ac0c   NOT FOUND.
12648430   eeffc0   NOT FOUND.
14598366   dec0de   NOT FOUND.
14600926   decade   NOT FOUND.
2147483647 ffffff7f NOT FOUND.
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


# version: 4.0
# resources: None

substitutions_2 = [('^((?!(FOUND.|Database\\s+encrypted)).)*$', ''), ('[ \t]+', ' ')]

init_script_2 = """
    recreate table test(x bigint unique);
    set term ^;
    create or alter procedure sp_delay as
        declare r bigint;
    begin
        r = rand() * 9223372036854775807;
        insert into test(x) values(:r);
        begin
            -- #########################################################
            -- #######################  D E L A Y  #####################
            -- #########################################################
            in autonomous transaction do
            insert into test(x) values(:r); -- this will cause delay because of duplicate in index
        when any do 
            begin
                -- nop --
            end
        end
    end
    ^
    set term ;^
    commit;

  """

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
# 
#  import os
#  import sys
#  import binascii
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  this_fdb = db_conn.database_name
#  
#  db_conn.execute_immediate('create sequence gen_ba0bab start with 12192683')
#  db_conn.execute_immediate('create sequence gen_badf00d start with 195948557')
#  db_conn.execute_immediate('create sequence gen_caca0  start with 830624')
#  db_conn.execute_immediate('create sequence gen_c0ffee start with 12648430')
#  db_conn.execute_immediate('create sequence gen_dec0de start with 14598366')
#  db_conn.execute_immediate('create sequence gen_decade start with 14600926')
#  db_conn.execute_immediate('create sequence gen_7FFFFFFF start with 2147483647')
#  db_conn.commit()
#  
#  # ::: NB ::: DO NOT close db_conn now! We can close it only after encryption will finish!
#  
#  ######################################################################################
#  
#  def check_page_for_readable_values(dbname, gen_page_number, pg_size, check_sequence_values):
#  
#      global binascii
#  
#      db_handle = open( dbname, "rb")
#      db_handle.seek( gen_page_number * pg_size )
#      page_content = db_handle.read( pg_size )
#      # read_binary_content( db_handle, gen_page_number * pg_size, pg_size )
#      db_handle.close()
#      page_as_hex=binascii.hexlify( page_content )
#  
#      # Iterate for each sequence value:
#      for n in check_sequence_values:
#  
#          # Get HEX representation of digital value.
#          # NOTE: format( 830624, 'x') is 'caca0' contains five (odd number!) characters.
#          hex_string = format(abs(n),'x')
#  
#          # Here we 'pad' hex representation to EVEN number of digits in it,
#          # otherwise binascii.hexlify fails with "Odd-length string error":
#          hex_string = ''.join( ('0' * ( len(hex_string)%2 ), hex_string ) )
#  
#          # ::: NOTE :::
#          # Generator value is stored in REVERSED bytes order.
#          # dec 830624 --> hex 0x0caca0 --> 0c|ac|a0 --> stored in page as three bytes: {a0; ac; 0c}
#  
#          # Decode string that is stored in variable 'hex_string' to HEX number,
#          # REVERSE its bytes and convert it to string again for further search
#          # in page content:
#          n_as_reversed_hex = binascii.hexlify( hex_string.decode('hex')[::-1] )
#  
#          print(n, n_as_reversed_hex, 'FOUND.' if n_as_reversed_hex in page_as_hex else 'NOT FOUND.' )
#          # print(n, n_as_reversed_hex, 'UNEXPECTEDLY FOUND AT POS. ' + '{:5d}'.format( page_as_hex.index(n_as_reversed_hex) ) if n_as_reversed_hex in page_as_hex else 'Not found (expected).' )
#  
#  ######################################################################################
#  
#  cur=db_conn.cursor()
#  get_current_seq_values='''
#      execute block returns( gen_curr bigint) as
#          declare gen_name rdb$generator_name;
#      begin
#          for
#              select rdb$generator_name from rdb$generators where rdb$system_flag is distinct from 1 order by rdb$generator_id
#              into gen_name
#          do begin
#              execute statement 'execute block returns(g bigint) as begin g = gen_id('|| gen_name ||', 0); suspend;  end' into gen_curr;
#              suspend;
#          end
#      end
#  '''
#  
#  # Obtain current values of user generators:
#  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  cur.execute(get_current_seq_values)
#  check_sequence_values=[]
#  for r in cur:
#      check_sequence_values += r[0],
#  #print('check_sequence_values=',check_sequence_values)
#  
#  
#  
#  # Obtain page size and number of generators page:
#  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  cur.execute('select m.mon$page_size,min(rdb$page_number) from mon$database m cross join rdb$pages p where p.rdb$page_type = 9 group by 1')
#  pg_size, gen_page_number = -1,-1
#  for r in cur:
#      pg_size=r[0]
#      gen_page_number=r[1]
#      # print(r[0],r[1])
#  
#  # 28.02.2021, temporary:
#  srv_mode='UNKNOWN'
#  cur.execute("select rdb$config_value from rdb$config where rdb$config_name='ServerMode'")
#  for r in cur:
#      srv_mode=r[0]
#  
#  cur.close()
#  db_conn.close()
#   
#  # Read gen page, convert it to hex and check whether generator values can be found there or no:
#  # Expected result: YES for all values because DB not encrypted now.
#  # ~~~~~~~~~~~~~~~
#  check_page_for_readable_values(this_fdb, gen_page_number, pg_size, check_sequence_values)
#  
#  
#  # 27.02.2021.
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  #      later it can be replaced with built-in plugin 'fbSampleDbCrypt'
#  #      but currently it is included only in FB 4.x builds (not in FB 3.x).
#  #      Discussed tih Dimitr, Alex, Vlad, letters since: 08-feb-2021 00:22
#  #      "Windows-distributive FB 3.x: it is desired to see sub-folder 'examples\\prebuild' with files for encryption, like it is in FB 4.x
#  #      *** DEFERRED ***
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else ( '"DbCrypt_example"' if db_conn.engine_version < 4 else '"fbSampleDbCrypt"' )
#  
#  sql_cmd='''
#      -- ################################################
#      -- ###    e n c r y p t      d a t a b a s e    ###
#      -- ################################################
#      alter database encrypt with %(PLUGIN_NAME)s key Red;
#      commit;
#  
#      -- 01.03.2021: we have to wait for several seconds
#      -- until encryption will be finished. But we must do
#      -- this delay within the same attachment as those that
#      -- launched encryption process.
#      -- The reason of that weird effect currently is unknown.
#      -- Here we make pause using 'set transaction lock timeout':
#  
#      -- 20.04.2021: increased delay from 2 to 3 seconds.
#      -- Otherwise can get "... crypt thread not complete":
#      set transaction lock timeout 3; -- THIS LOCK TIMEOUT SERVES ONLY FOR DELAY
#      execute procedure sp_delay;
#      rollback;
#      show database;
#      quit;
#  ''' % locals()
#  
#  runProgram('isql', [ dsn ], sql_cmd)
#  
#  # Read again gen page, convert it to hex and check whether generator values can be found there or no.
#  # Expected result: NOT FOUND, for all values (because DB was encrypted).
#  # ~~~~~~~~~~~~~~~~
#  check_page_for_readable_values(this_fdb, gen_page_number, pg_size, check_sequence_values)
#  
#    
#---
#act_2 = python_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
12192682    aa0bba    FOUND.
195948556   0cf0ad0b  FOUND.
830623      9fac0c    FOUND.
12648429    edffc0    FOUND.
14598365    ddc0de    FOUND.
14600925    ddcade    FOUND.
2147483646  feffff7f  FOUND.

Database encrypted

12192682    aa0bba    NOT FOUND.
195948556   0cf0ad0b  NOT FOUND.
830623      9fac0c    NOT FOUND.
12648429    edffc0    NOT FOUND.
14598365    ddc0de    NOT FOUND.
14600925    ddcade    NOT FOUND.
2147483646  feffff7f  NOT FOUND.
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_2(db_2):
    pytest.fail("Test not IMPLEMENTED")


