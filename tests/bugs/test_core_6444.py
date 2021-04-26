#coding:utf-8
#
# id:           bugs.core_6444
# title:        Ability to query Firebird configuration using SQL
# decription:   
#                   Test found FB_HOME directory and makes copy its firebird.conf and database.conf files.
#                   Then it found free TCP port and overwrites content of firebird.conf: this new port 
#                   will be specified for RemoveServicePort and some other parameters also will be added.
#                   File <FB_HOME>\\databases.conf is also changed: we add new alias for database that will
#                   be self-security and specify lot of per-database parameters for it.
#                   Some numeric parameters intentionally will be assigned to huge bigint values, namely:
#                       * FileSystemCacheThreshold
#                       * TempCacheLimit
#                   Their huge values do not affect on actual work; this is done only for check proper
#                   interpretation of them.
#                   
#                   After this test launches Firebird as application (see async. call of Popen()) and make
#                   connect to new database by launching ISQL.
#                   When connect is established, we query RDB$CONFIG table two times:
#                       * as SYSDBA (in this case all config parameters and their actual values must be seen);
#                       * as NON-privileged user (zero rows must be issued for query to RDB$CONFIG).
#                   
#                   Finally (after return from ISQL) test terminates Firebird application process.
#                   Checked on 4.0.0.2365.
#               
#                   ::: CAUTION-1 :::
#                   This test will fail if new parameter will appear in firebird.conf or if old one removed from there.
#                   One need to adjust expected_stdout in this case.
#               
#                   ::: CAUTION-2 :::
#                   Windows Firewall can block attempt to launch FB as application (dialog window appears in this case).
#                   One may need to configure Firewall so that process <FB_HOME>
#               irebird.exe is enable to operate on any port.
#               
#                   Perhaps, following command will be useful: netsh advfirewall set privateprofile state off
#               
#                   ::: CAUTION-3 :::
#                   13.02.2021 Currently this test must be executed only on Windows!
#                   On Linux it terminates with runtime ERROR ('E') and firebird.conf + databases.conf remains in $FB_HOME
#                   with changed parameters.
#                   For Classic this prevents all subsequent tests to be executed normally: all of them will also finish with 'E'.
#                   This problem will be solved later.
#                
# tracker_id:   CORE-6444
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('[=]+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import sys
#  import os
#  import shutil
#  import time
#  import datetime
#  import tempfile
#  import subprocess
#  from fdb import services
#  
#  #--------------------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#  
#  #--------------------------------------------
#  
#  def find_free_port():
#      import socket
#      from contextlib import closing
#      # AF_INET - constant represent the address (and protocol) families, used for the first argument to socket()
#      # A pair (host, port) is used for the AF_INET address family, where host is a string representing either a 
#      # hostname in Internet domain notation like 'daring.cwi.nl' or an IPv4 address like '100.50.200.5', and port is an integer.
#      # SOCK_STREAM means that it is a TCP socket.
#      # SOCK_DGRAM means that it is a UDP socket.
#      with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
#          s.bind(('', 0))
#          s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#          return s.getsockname()[1]
#  
#  #--------------------------------------------
#  
#  FB_HOME = services.connect(host='localhost', user=user_name, password=user_password).get_home_directory()
#  
#  fb_vers = str(db_conn.engine_version)[:1] # character for security.db file: engine = 4.0  --> '4'
#  sec_db = FB_HOME + 'security' + fb_vers+ '.fdb'
#  
#  db_conn.close()
#  
#  fdb_test = os.path.join(context['temp_directory'],'tmp_c6444.fdb')
#  
#  dts = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
#  
#  fbconf_cur = os.path.join(FB_HOME, 'firebird.conf')
#  fbconf_bak = os.path.join(context['temp_directory'], 'firebird_'+dts+'.bak')
#  
#  dbconf_cur = os.path.join(FB_HOME, 'databases.conf')
#  dbconf_bak = os.path.join(context['temp_directory'], 'databases_'+dts+'.bak')
#  
#  shutil.copy2( fbconf_cur, fbconf_bak )
#  shutil.copy2( dbconf_cur, dbconf_bak )
#  
#  shutil.copy2( sec_db, fdb_test )
#  
#  TMPDIR = os.path.join( FB_HOME, 'examples' ) # tempfile.gettempdir()
#  TMP_FREE_PORT = find_free_port()
#  #TMP_FREE_PORT = 57456
#  
#  cfg_params_to_change= {
#      'AllowEncryptedSecurityDatabase' : 'true'
#     ,'AuthClient' : 'Srp'
#     ,'AuthServer' : 'Legacy_Auth, Srp'
#     ,'BugcheckAbort' : '1'
#     ,'ClientBatchBuffer' : '256k'
#     ,'ConnectionIdleTimeout' : '77' # will be also specified in databases.conf; effective value must be from databases.conf, NOT from here!
#     ,'ConnectionTimeout' : '123'
#     ,'DeadlockTimeout' : '15'
#     ,'DatabaseAccess' : 'None'      # In order to display only ALIAS of database rather than its full name
#     ,'DefaultDbCachePages' : '1234' # will be also specified in databases.conf; effective value must be from databases.conf, NOT from here!
#     ,'DefaultTimeZone' : '-7:00'
#     ,'DummyPacketInterval' : '11'
#     ,'EventMemSize' : '12321'
#     ,'ExtConnPoolLifeTime' : '1212'
#     ,'ExtConnPoolSize' : '123'
#     ,'FileSystemCacheThreshold' : '8589934591G'
#     ,'IpcName' : 'fb4x_tmp_c6444'
#     ,'IPv6V6Only' : '1'
#     ,'InlineSortThreshold' : '8k'
#     ,'LockHashSlots' : '33333' # will be also specified in databases.conf; effective value must be from databases.conf, NOT from here!
#     ,'LockMemSize' : '17m'     # will be also specified in databases.conf; effective value must be from databases.conf, NOT from here!
#     ,'MaxUserTraceLogSize' : '100'
#     ,'ReadConsistency' : '0'
#     ,'RemoteServiceName' : 'tmp_fbs_6444'
#     ,'RemoteServicePort' : str(TMP_FREE_PORT)
#     ,'ServerMode' : 'SuperClassic'
#     ,'StatementTimeout' : '777' # will be also specified in databases.conf; effective value must be from databases.conf, NOT from here!
#     ,'TcpLoopbackFastPath' : '0'
#     ,'TcpNoNagle' : 'false'
#     ,'TcpRemoteBufferSize' : '5555'
#     ,'TempBlockSize' : '5m'
#     ,'TempDirectories' : os.path.normpath( TMPDIR )
#     ,'UDFaccess' : 'Restrict UDF'
#     ,'UseFileSystemCache' : 'false'
#     ,'WireCompression' : 'true'
#     ,'WireCrypt' : 'Required'
#     ,'WireCryptPlugin' : 'Arc4'
#  
#  }
#  
#  f_fbconf=open( fbconf_cur, 'w')
#  for k,v in sorted(cfg_params_to_change.items()):
#      f_fbconf.write( ''.join( (k, ' = ', v, '\\n') ) )
#  flush_and_close( f_fbconf )
#  
#  alias_data='''
#      # Added temporarily for executing test core_6444.fbt
#      tmp_6444 = %(fdb_test)s {
#  
#          SecurityDatabase = tmp_6444
#  
#          RemoteAccess = true
#          DatabaseGrowthIncrement = 123m
#          DataTypeCompatibility = 3.0
#          DefaultDbCachePages = 4321
#          ClearGTTAtRetaining = 1
#          
#          # Set number of minutes after which idle attachment will be disconnected by the engine. Zero means no timeout is set.
#          ConnectionIdleTimeout = 99
#  
#          ExternalFileAccess = Full
#  
#          LockHashSlots = 49999
#          LockMemSize = 29m
#  
#          MaxIdentifierByteLength = 31
#          MaxIdentifierCharLength = 31
#          MaxUnflushedWrites = 111
#          MaxUnflushedWriteTime = 15
#          
#          Providers = Engine13, Remote
#  
#          SnapshotsMemSize = 99m
#  
#          # Set number of seconds after which statement execution will be automatically cancelled by the engine. Zero means no timeout is set.
#          StatementTimeout = 999
#  
#          TempBlockSize = 3m
#          TempCacheLimit = 8589934591G
#          
#          TipCacheBlockSize = 3m
#  
#          UserManager = Legacy_UserManager, Srp
#      }
#  ''' % locals()
#  
#  f_dbconf=open( dbconf_cur, 'w')
#  f_dbconf.write(alias_data)
#  flush_and_close( f_dbconf )
#  
#  p_tmp_fb_pid = subprocess.Popen( [ FB_HOME+'firebird', '-a'] )
#  
#  time.sleep(2)
#  
#  sql_text='''
#      -- set echo on;
#      set wng off;
#      connect 'tmp_6444';
#      create or alter user sysdba password 'masterkey' using plugin Srp;
#      create or alter user tmp$c6444 password '123' using plugin Srp;
#      revoke all on all from tmp$c6444;
#      create or alter view v_config as
#      select
#           g.rdb$config_name param_name
#          ,iif(trim(g.rdb$config_value)='', '[empty]'
#               ,iif(  g.rdb$config_name = 'TempDirectories' and upper(g.rdb$config_value) = upper('%(TMPDIR)s') or g.rdb$config_name = 'RemoteServicePort' and g.rdb$config_value = %(TMP_FREE_PORT)s
#                     ,'[MATCHES]'
#                     ,g.rdb$config_value)
#              ) param_value
#          ,iif(trim(g.rdb$config_default)='', '[empty]', replace(g.rdb$config_default,'%(FB_HOME)s','') ) param_default
#          ,g.rdb$config_is_set param_is_set
#          ,g.rdb$config_source param_source
#      from rdb$config g
#      order by param_name
#      ;
#      commit;
#      grant select on v_config to tmp$c6444;
#      commit;
#  
#      connect 'localhost/%(TMP_FREE_PORT)s:tmp_6444' user sysdba password 'masterkey';
#  
#      set count on;
#      set width param_name 50;
#      set width param_value 64;
#      set width param_default 64;
#      set width param_source 64;
#  
#      select * from v_config; -- SYSDBA: must see all parameters with their effective values
#  
#      commit;
#      connect 'localhost/%(TMP_FREE_PORT)s:tmp_6444' user tmp$c6444 password '123';
#      
#      select * from v_config; -- NON-PRIVILEGED user: must see 0 rows
#  
#      /*
#      -- for debug only:
#      set list on;
#      select
#          current_user as who_am_i
#          ,m.mon$database_name as db_name
#          ,m.mon$page_buffers as db_buffers
#          ,m.mon$sec_database as db_sec_name
#          ,a.mon$remote_protocol
#          ,a.mon$idle_timeout
#          ,a.mon$statement_timeout
#          ,a.mon$wire_compressed
#          ,a.mon$wire_encrypted
#          ,a.mon$wire_crypt_plugin
#      from mon$database m
#      cross join mon$attachments a
#      where a.mon$attachment_id = current_connection
#      ;
#      */
#  
#      commit;
#      connect 'localhost/%(TMP_FREE_PORT)s:tmp_6444' user sysdba password 'masterkey';
#      drop user tmp$c6444 using plugin Srp;
#      commit;
#  
#  ''' % locals()
#  
#  f_sql_cmd = open( os.path.join(context['temp_directory'],'tmp_c6444.sql'), 'w')
#  f_sql_cmd.write( sql_text )
#  flush_and_close( f_sql_cmd )
#  
#  f_sql_log=open( os.path.join(context['temp_directory'],'tmp_c6444.log'), 'w')
#  f_sql_err=open( os.path.join(context['temp_directory'],'tmp_c6444.err'), 'w')
#  
#  #subprocess.call( [FB_HOME+'isql', 'localhost/%(TMP_FREE_PORT)s:tmp_6444' % locals(), '-i', f_sql_cmd.name], stdout=f_sql_log, stderr=f_sql_err )
#  subprocess.call( [FB_HOME+'isql', '-q', '-pag', '999999', '-i', f_sql_cmd.name, '-user', 'SYSDBA'], stdout=f_sql_log, stderr=f_sql_err )
#  
#  flush_and_close( f_sql_log )
#  flush_and_close( f_sql_err )
#  
#  p_tmp_fb_pid.terminate()
#  
#  shutil.move( fbconf_bak, fbconf_cur )
#  shutil.move( dbconf_bak, dbconf_cur )
#  
#  
#  with open(f_sql_err.name, 'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED STDERR: ' + line)
#  
#  with open(f_sql_log.name, 'r') as f:
#      for line in f:
#          if line.split():
#              print(line)
#  
#  time.sleep(1)
#  
#  f_list=( f_sql_log, f_sql_err, f_sql_cmd )
#  
#  # Cleanup
#  ##########
#  cleanup( [ i.name for i in f_list ] + [fdb_test] )
#  
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PARAM_NAME                                         PARAM_VALUE                                                      PARAM_DEFAULT                                                    PARAM_IS_SET PARAM_SOURCE                                                     
    ================================================== ================================================================ ================================================================ ============ ================================================================ 
    AllowEncryptedSecurityDatabase                     true                                                             false                                                            <true>       firebird.conf                                                    
    AuditTraceConfigFile                               [empty]                                                          [empty]                                                          <false>      <null>                                                           
    AuthClient                                         Srp                                                              Srp256, Srp, Win_Sspi, Legacy_Auth                               <true>       firebird.conf                                                    
    AuthServer                                         Legacy_Auth, Srp                                                 Srp256                                                           <true>       firebird.conf                                                    
    BugcheckAbort                                      true                                                             false                                                            <true>       firebird.conf                                                    
    ClearGTTAtRetaining                                true                                                             false                                                            <true>       databases.conf                                                   
    ClientBatchBuffer                                  262144                                                           131072                                                           <true>       firebird.conf                                                    
    ConnectionIdleTimeout                              99                                                               0                                                                <true>       databases.conf                                                   
    ConnectionTimeout                                  123                                                              180                                                              <true>       firebird.conf                                                    
    CpuAffinityMask                                    0                                                                0                                                                <false>      <null>                                                           
    DataTypeCompatibility                              3.0                                                              <null>                                                           <true>       databases.conf                                                   
    DatabaseAccess                                     None                                                             Full                                                             <true>       firebird.conf                                                    
    DatabaseGrowthIncrement                            128974848                                                        134217728                                                        <true>       databases.conf                                                   
    DeadlockTimeout                                    15                                                               10                                                               <true>       firebird.conf                                                    
    DefaultDbCachePages                                4321                                                             2048                                                             <true>       databases.conf                                                   
    DefaultTimeZone                                    -7:00                                                            <null>                                                           <true>       firebird.conf                                                    
    DummyPacketInterval                                11                                                               0                                                                <true>       firebird.conf                                                    
    EventMemSize                                       12321                                                            65536                                                            <true>       firebird.conf                                                    
    ExtConnPoolLifeTime                                1212                                                             7200                                                             <true>       firebird.conf                                                    
    ExtConnPoolSize                                    123                                                              0                                                                <true>       firebird.conf                                                    
    ExternalFileAccess                                 Full                                                             None                                                             <true>       databases.conf                                                   
    FileSystemCacheSize                                0                                                                0                                                                <false>      <null>                                                           
    FileSystemCacheThreshold                           9223372035781033984                                              65536                                                            <true>       firebird.conf                                                    
    GCPolicy                                           combined                                                         combined                                                         <false>      <null>                                                           
    GuardianOption                                     1                                                                1                                                                <false>      <null>                                                           
    IPv6V6Only                                         true                                                             false                                                            <true>       firebird.conf                                                    
    InlineSortThreshold                                8192                                                             1000                                                             <true>       firebird.conf
    IpcName                                            fb4x_tmp_c6444                                                   FIREBIRD                                                         <true>       firebird.conf                                                    
    KeyHolderPlugin                                    [empty]                                                          [empty]                                                          <false>      <null>                                                           
    LegacyHash                                         true                                                             true                                                             <false>      <null>                                                           
    LockAcquireSpins                                   0                                                                0                                                                <false>      <null>                                                           
    LockHashSlots                                      49999                                                            8191                                                             <true>       databases.conf                                                   
    LockMemSize                                        30408704                                                         1048576                                                          <true>       databases.conf                                                   
    MaxIdentifierByteLength                            31                                                               252                                                              <true>       databases.conf                                                   
    MaxIdentifierCharLength                            31                                                               63                                                               <true>       databases.conf                                                   
    MaxUnflushedWriteTime                              15                                                               5                                                                <true>       databases.conf                                                   
    MaxUnflushedWrites                                 111                                                              100                                                              <true>       databases.conf                                                   
    MaxUserTraceLogSize                                100                                                              10                                                               <true>       firebird.conf                                                    
    OutputRedirectionFile                              nul                                                              nul                                                              <false>      <null>                                                           
    ProcessPriorityLevel                               0                                                                0                                                                <false>      <null>                                                           
    Providers                                          Engine13, Remote                                                 Remote, Engine13, Loopback                                       <true>       databases.conf                                                   
    ReadConsistency                                    false                                                            true                                                             <true>       firebird.conf                                                    
    Redirection                                        false                                                            false                                                            <false>      <null>                                                           
    RelaxedAliasChecking                               false                                                            false                                                            <false>      <null>                                                           
    RemoteAccess                                       true                                                             true                                                             <true>       databases.conf                                                   
    RemoteAuxPort                                      0                                                                0                                                                <false>      <null>                                                           
    RemoteBindAddress                                  <null>                                                           <null>                                                           <false>      <null>                                                           
    RemoteFileOpenAbility                              false                                                            false                                                            <false>      <null>                                                           
    RemotePipeName                                     interbas                                                         interbas                                                         <false>      <null>                                                           
    RemoteServiceName                                  tmp_fbs_6444                                                     gds_db                                                           <true>       firebird.conf                                                    
    RemoteServicePort                                  [MATCHES]                                                        0                                                                <true>       firebird.conf                                                    
    SecurityDatabase                                   tmp_6444                                                         security4.fdb                                                    <true>       databases.conf                                                   
    ServerMode                                         SuperClassic                                                     Super                                                            <true>       firebird.conf                                                    
    SnapshotsMemSize                                   103809024                                                        65536                                                            <true>       databases.conf                                                   
    StatementTimeout                                   999                                                              0                                                                <true>       databases.conf                                                   
    TcpLoopbackFastPath                                false                                                            true                                                             <true>       firebird.conf                                                    
    TcpNoNagle                                         false                                                            true                                                             <true>       firebird.conf                                                    
    TcpRemoteBufferSize                                5555                                                             8192                                                             <true>       firebird.conf                                                    
    TempBlockSize                                      5242880                                                          1048576                                                          <true>       firebird.conf                                                   
    TempCacheLimit                                     9223372035781033984                                              67108864                                                         <true>       databases.conf                                                   
    TempDirectories                                    [MATCHES]                                                        <null>                                                           <true>       firebird.conf                                                    
    TipCacheBlockSize                                  3145728                                                          4194304                                                          <true>       databases.conf                                                   
    TraceDSQL                                          0                                                                0                                                                <false>      <null>                                                           
    TracePlugin                                        fbtrace                                                          fbtrace                                                          <false>      <null>                                                           
    UdfAccess                                          Restrict UDF                                                     None                                                             <true>       firebird.conf                                                    
    UseFileSystemCache                                 false                                                            true                                                             <true>       firebird.conf                                                    
    UserManager                                        Legacy_UserManager, Srp                                          Srp                                                              <true>       databases.conf                                                   
    WireCompression                                    true                                                             false                                                            <true>       firebird.conf                                                    
    WireCrypt                                          Required                                                         Required                                                         <true>       firebird.conf                                                    
    WireCryptPlugin                                    Arc4                                                             ChaCha, Arc4                                                     <true>       firebird.conf                                                    

    Records affected: 70
    Records affected: 0
  """

@pytest.mark.version('>=4.0')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_6444_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


