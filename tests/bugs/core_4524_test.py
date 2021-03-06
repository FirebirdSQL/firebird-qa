#coding:utf-8
#
# id:           bugs.core_4524
# title:        New gbak option to enable encryption during restore
# decription:   
#                   Part of this test was copied from core_6071.fbt.
#                   We create new database and try to encrypt it using IBSurgeon Demo Encryption package
#                   ( https://ib-aid.com/download-demo-firebird-encryption-plugin/ ; https://ib-aid.com/download/crypt/CryptTest.zip )
#                   License file plugins\\dbcrypt.conf with unlimited expiration was provided by IBSurgeon to Firebird Foundation (FF).
#                   This file was preliminary stored in FF Test machine.
#                   Test assumes that this file and all neccessary libraries already were stored into FB_HOME and %FB_HOME%\\plugins.
#               
#                   We create several generators in the test DB and get number of generators page using query to RDB$PAGES (page_type=9).
#                   Also we get page_size and using these data we can obtain binary content of generatord page. This content futher is parsed
#                   in order to verify that generators names are readable (while DB is not yet encrypted).
#               
#                   Then we encrypt DB and make delay after this for ~1..2 seconds BEFORE detach from database.
#               
#                   After this we:
#                   1. Change temp DB state to full shutdown and bring it online - in order to be sure that we will able to drop this file later;
#                   2. Make backup of this temp DB, using gbak utility and '-KEYHOLDER <name_of_key_holder>' command switch.
#                   3. Make restore from just created backup.
#                   4. Make validation of just restored database by issuing command "gfix -v -full ..."
#                      ( i.e. validate both data and metadata rather than online val which can check user data only).
#                   5. Open restored DB as binary file and attempt to read again generators names - this must fail, their names must be encrypted.
#                   6. Check that NO errors occured on any above mentioned steps. Also check that backup and restore STDOUT logs contain expected 
#                      text about successful completition
#               
#                   13.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 4.0.0.2416
#                     Linux:   4.0.0.2416
#                   Note: different names for encryption plugin and keyholde rare used for Windows vs Linux:
#                      PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else '"fbSampleDbCrypt"'
#                      KHOLDER_NAME = 'KeyHolder' if os.name == 'nt' else "fbSampleKeyHolder"
#               
#                
# tracker_id:   CORE-4524
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('\\d+ BYTES WRITTEN', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  import binascii
#  import re
#  import fdb
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  #--------------------------------------------
#  
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_4524.encrypted.fdb'
#  tmpres='$(DATABASE_LOCATION)'+'tmp_core_4524.restored.fdb'
#  tmpbkp='$(DATABASE_LOCATION)'+'tmp_core_4524.encrypted.fbk'
#  
#  cleanup( (tmpfdb, tmpres) )
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb )
#  
#  con.execute_immediate('create sequence gen_ba0bab start with 12192683')
#  con.execute_immediate('create sequence gen_badf00d start with 195948557')
#  con.execute_immediate('create sequence gen_caca0  start with 830624')
#  con.execute_immediate('create sequence gen_c0ffee start with 12648430')
#  con.execute_immediate('create sequence gen_dec0de start with 14598366')
#  con.execute_immediate('create sequence gen_decade start with 14600926')
#  con.execute_immediate('create sequence gen_7FFFFFFF start with 2147483647')
#  con.commit()
#  
#  cur=con.cursor()
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
#  # Obtain page size and number of generators page:
#  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  cur.execute('select m.mon$page_size,min(rdb$page_number) from mon$database m cross join rdb$pages p where p.rdb$page_type = 9 group by 1')
#  pg_size, gen_page_number = -1,-1
#  for r in cur:
#      pg_size=r[0]
#      gen_page_number=r[1]
#      # print(r[0],r[1])
#  cur.close()
#  
#  
#  # Read gen page, convert it to hex and check whether generator values can be found there or no:
#  # Expected result: YES for all values because DB not encrypted now.
#  # ~~~~~~~~~~~~~~~
#  check_page_for_readable_values(tmpfdb, gen_page_number, pg_size, check_sequence_values)
#  
#  ################################################
#  ###    e n c r y p t      d a t a b a s e    ###
#  ################################################
#  
#  # 14.04.2021.
#  # Name of encryption plugin depends on OS:
#  # * for Windows we (currently) use plugin by IBSurgeon, its name is 'dbcrypt';
#  # * for Linux we use:
#  #   ** 'DbCrypt_example' for FB 3.x
#  #   ** 'fbSampleDbCrypt' for FB 4.x+
#  #
#  PLUGIN_NAME = 'dbcrypt' if os.name == 'nt' else '"fbSampleDbCrypt"'
#  KHOLDER_NAME = 'KeyHolder' if os.name == 'nt' else "fbSampleKeyHolder"
#  cur = con.cursor()
#  cur.execute('alter database encrypt with %(PLUGIN_NAME)s key Red' % locals())
#  ### DOES NOT WORK ON LINUX! ISSUES 'TOKEN UNKNOWN' !! >>> con.execute_immediate('alter database encrypt with %(PLUGIN_NAME)s key Red' % locals()) // sent letter to Alex and dimitr, 14.04.2021
#  con.commit()
#  time.sleep(2)
#  #          ^
#  #          +-------- !! ALLOW BACKGROUND ENCRYPTION PROCESS TO COMPLETE ITS JOB !!
#  
#  #######################################
#  # Added 14.04.2021: check that database is actually encrypted.
#  # Column MON$DATABASE.MON$CRYPT_STATE can have following values:
#  # 0 = NOT encrypteed;
#  # 1 = encrypted
#  # 2 = encryption process is running now
#  # 3 = decryption process is running now
#  #######################################
#  cur.execute("select iif(mon$crypt_state=1, 'Database ENCRYPTED.', '### ERROR: DATABASE REMAINS UNENCRYPTED ###, MON$CRYPT_STATE = ' || mon$crypt_state) as msg from mon$database")
#  for r in cur:
#      print( r[0] )
#  con.close()
#  cur.close()
#  
#  #-------------------------- shutdown temp DB and bring it online --------------------
#  
#  f_dbshut_log = open( os.path.join(context['temp_directory'],'tmp_dbshut_4524.log'), 'w')
#  subprocess.call( [ context['gfix_path'], 'localhost:'+tmpfdb, "-shut", "full", "-force", "0" ],
#                   stdout = f_dbshut_log,
#                   stderr = subprocess.STDOUT
#                 )
#  subprocess.call( [ context['gfix_path'], 'localhost:'+tmpfdb, "-online" ],
#                   stdout = f_dbshut_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_dbshut_log )
#  
#  #--------------------------- backup and restore --------------------------------------
#  fn_bkp_log=open( os.path.join(context['temp_directory'],'tmp_backup_4524.log'), 'w')
#  fn_bkp_err=open( os.path.join(context['temp_directory'],'tmp_backup_4524.err'), 'w')
#  
#  # /var/tmp/fb40tmp/bin/gbak -b -v -keyholder fbSampleKeyHolder -crypt fbSampleDbCrypt localhost:/path/to/encrypted.fdb /path/to/encrypted.fbk
#  
#  subprocess.call([ context['gbak_path']
#                   ,"-b"
#                   ,"-v"
#                   ,"-KEYHOLDER", KHOLDER_NAME  # "KeyHolder" | "fbSampleKeyHolder"
#                   ,"-crypt", PLUGIN_NAME.replace('"','')       # DbCrypt | fbSampleDbCrypt
#                   ,'localhost:' + tmpfdb
#                   ,tmpbkp
#                  ],
#                  stdout=fn_bkp_log, stderr=fn_bkp_err)
#  
#  flush_and_close( fn_bkp_log )
#  flush_and_close( fn_bkp_err )
#  
#  
#  fn_res_log=open( os.path.join(context['temp_directory'],'tmp_restore_4524.log'), 'w')
#  fn_res_err=open( os.path.join(context['temp_directory'],'tmp_restore_4524.err'), 'w')
#  
#  # C:\\FB SS\\gbak.exe -rep -KEYHOLDER KeyHolder C:\\FBTESTING\\qa\\misc\\C4524.fbk /:C:\\FBTESTING\\qa\\misc\\c4524.restored.FDB
#  subprocess.call([ context['gbak_path']
#                   ,"-rep"
#                   ,"-v"
#                   ,"-KEYHOLDER", KHOLDER_NAME  # "KeyHolder" | "fbSampleKeyHolder"
#                   ,tmpbkp
#                   ,'localhost:' + tmpres
#                  ],
#                  stdout=fn_res_log, stderr=fn_res_err)
#  
#  flush_and_close( fn_res_log )
#  flush_and_close( fn_res_err )
#  
#  #-------------------------- validate just restored database --------------------
#  
#  f_valid_log = open( os.path.join(context['temp_directory'],'tmp_valid_4524.log'), 'w')
#  subprocess.call( [ context['gfix_path'], 'localhost:'+tmpres, "-v", "-full" ],
#                   stdout = f_valid_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_valid_log )
#  
#  #-----------------------------------------------
#  
#  # Read gen page in RESTORED database, convert it to hex and check whether generator values can be found there or no.
#  # Expected result: NOT for all values because DB was encrypted.
#  # ~~~~~~~~~~~~~~~~
#  check_page_for_readable_values(tmpres, gen_page_number, pg_size, check_sequence_values)
#  
#  #-----------------------------------------------
#  
#  # Check that all was fine:
#  
#  with open(f_dbshut_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED SHUTDOWN OUTPUT: ' + line)
#  
#  with open(fn_bkp_err.name,'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED BACKUP STDERR: ' + line)
#  
#  with open(fn_res_err.name,'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED RESTORE STDERR: ' + line)
#  
#  with open(f_dbshut_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED VALIDATION OUTPUT: ' + line)
#  
#  
#  # gbak -b should finish with line:
#  #    gbak:closing file, committing, and finishing. 512 bytes written
#  gbak_backup_finish_ptn=re.compile('gbak:closing\\s+file,\\s+committing,\\s+and\\s+finishing.*', re.IGNORECASE)
#  with open(fn_bkp_log.name,'r') as f:
#      for line in f:
#          if gbak_backup_finish_ptn.search(line):
#              print('EXPECTED BACKUP FINISH FOUND: '+line.upper() )
#  
#  
#  # gbak -c should finish with lines:
#  #    gbak:finishing, closing, and going home
#  #    gbak:adjusting the ONLINE and FORCED WRITES flags
#  
#  gbak_restore_finish_ptn=re.compile('gbak:adjusting\\s+the\\s+ONLINE\\s+and\\s+FORCED\\s+WRITES\\s+.*', re.IGNORECASE)
#  with open(fn_res_log.name,'r') as f:
#      for line in f:
#          if gbak_restore_finish_ptn.search(line):
#              print('EXPECTED RESTORE FINISH FOUND: '+line.upper() )
#  
#  
#  # cleanup
#  ##########
#  time.sleep(1)
#  f_list = [ i.name for i in ( f_dbshut_log, fn_bkp_log, fn_bkp_err, fn_res_log, fn_res_err, f_valid_log ) ] + [ tmpfdb, tmpres, tmpbkp ]
#  cleanup( f_list )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    12192682 aa0bba FOUND.
    195948556 0cf0ad0b FOUND.
    830623 9fac0c FOUND.
    12648429 edffc0 FOUND.
    14598365 ddc0de FOUND.
    14600925 ddcade FOUND.
    2147483646 feffff7f FOUND.

    Database ENCRYPTED.

    12192682 aa0bba NOT FOUND.
    195948556 0cf0ad0b NOT FOUND.
    830623 9fac0c NOT FOUND.
    12648429 edffc0 NOT FOUND.
    14598365 ddc0de NOT FOUND.
    14600925 ddcade NOT FOUND.
    2147483646 feffff7f NOT FOUND.
    EXPECTED BACKUP FINISH FOUND: GBAK:CLOSING FILE, COMMITTING, AND FINISHING.
    EXPECTED RESTORE FINISH FOUND: GBAK:ADJUSTING THE ONLINE AND FORCED WRITES FLAGS
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


