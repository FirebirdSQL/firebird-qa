#coding:utf-8
#
# id:           bugs.core_6048
# title:        Provide ability to see current state of DB encryption
# decription:   
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
#                   Checked on:
#                       4.0.0.1575: OK, 3.024s.
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
# tracker_id:   CORE-6048
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  
#  
#  sql_scrypt='''
#      set list on;
#      recreate table test(x bigint unique);
#      set term ^;
#      create or alter procedure sp_delay as
#          declare r bigint;
#      begin
#          r = rand() * 9223372036854775807;
#          insert into test(x) values(:r);
#          begin
#              -- #########################################################
#              -- #######################  D E L A Y  #####################
#              -- #########################################################
#              in autonomous transaction do
#              insert into test(x) values(:r); -- this will cause delay because of duplicate in index
#          when any do 
#              begin
#                  -- nop --
#              end
#          end
#      end
#      ^
#      set term ;^
#      commit;
#  
#      alter database encrypt with %(PLUGIN_NAME)s key Red;
#      commit;
#      set transaction lock timeout 2; -- THIS LOCK TIMEOUT SERVES ONLY FOR DELAY
#      execute procedure sp_delay;
#      rollback;
#      select mon$crypt_state as "Is database encrypted ?" from mon$database;
#      commit;
#  
#      alter database decrypt;
#      commit;
#      set transaction lock timeout 2; -- THIS LOCK TIMEOUT SERVES ONLY FOR DELAY
#      execute procedure sp_delay;
#      rollback;
#      select mon$crypt_state as "Is database encrypted ?" from mon$database;
#  ''' % locals()
#  
#  f_sql_cmd = open(os.path.join(context['temp_directory'],'tmp_core_6048.sql'), 'w')
#  f_sql_cmd.write(sql_scrypt)
#  flush_and_close( f_sql_cmd )
#  
#  f_sql_log = open( os.path.join(context['temp_directory'],'tmp_core_6048.log'), 'w')
#  
#  subprocess.call( [ context['isql_path'], dsn, "-n", "-q", "-i", f_sql_cmd.name ],
#                     stdout = f_sql_log,
#                     stderr = subprocess.STDOUT
#                  )
#  flush_and_close( f_sql_log )
#  
#  with open(f_sql_log.name,'r') as f:
#     for line in f:
#         print(line)
#  
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_sql_cmd,f_sql_log) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Is database encrypted ?         1
    Is database encrypted ?         0
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


