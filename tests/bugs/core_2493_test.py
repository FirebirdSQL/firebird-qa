#coding:utf-8
#
# id:           bugs.core_2493
# title:        Append the IP address of the remote host to error messages in firebird.log for TCP connections
# decription:   
#                  Following actions are performed by this test:
#                  
#                  1. Obtain current firebird.log and saves it to the file with name = 'tmp_2493_fblog_before.txt';
#                  
#                  2. Asynchronously launch ISQL in child process with request to return client IP address (via asking context variable)
#                     and after this - do some 'heavy query' that for sure will take a lot of time and resources.
#                     Output is redirected to file with name = 'tmp_2493_isql.log' and will be parsed further (we'll search for client IP there).
#                  
#                  3. Kill launched ISQL process after several seconds. At this point new message must appear in firebird.log and it MUST
#                     be in format described in the ticket. Because this abend will be detected by SERVER, format of message will be like this:
#                     (for TCPv4):  INET/inet_error: read errno = 10054, client host = prog1, address = 127.0.0.1/4076, user = john
#                     (for TCPv6):  INET/inet_error: read errno = 10054, client host = prog2, address = fe80::c40e:21ec:b5c7:8963/56831, user = mick
#                  
#                  4. Wait several seconds and after it - obtain again firebird.log (new content) and save it in 'tmp_2493_fblog_after.txt'.
#                  
#                  5. Make file comparison by calling method from standard Python tool - difflib. Result of this comparison will be stored
#                     in file with name 'tmp_2493_diff.txt'. This file will have several lines from which we are interested only for one which
#                     STARTS with "+" (PLUS sign) and does contain phrase 'INET/INET_ERROR'. Diff-file must contain only ONE such line.
#                  
#                  6. Next we parse this line: remove "/" and "="characters from it and split then text into array of words:
#                     + INET inet_error read errno 10054 client host prog1 address 127.0.0.1 4417   user john ------- for IPv4
#                     0  1       2       3    4      5     6     7     8       9       10      11     12   13
#                     + INET inet_error read errno 10054 client host prog2 address x::y:z:u:v 56831 user mick ------- for IPv6
#                  7. Then we scan this array backward and check tokens for matching simple rules (N = array len):
#                     * token N-1 must be OS user name; this name can be followed by some kind of "suffix": "JOHN.-1.-1" - and we have to take only 1st word from it.
#                       NB: we current OS user using call of getpass.getuser(). It must be compared in case insensitive manner;
#                     * token N-2 is just word "user" (as is);
#                     * token N-3 is port number, it has to be positive value;
#                     * token N-4 is IP. It must be equal to rdb$get_context('SYSTEM','CLIENT_ADDRESS').
#               
#                     This is how differences look in firebird.log:
#                     # 2.5.9:
#                     #       INET/inet_error: read errno = 10054, client address = 127.0.0.1 3268, user ZOTOV.-1.-1
#                     #                                                                   ^    ^    ^      ^
#                     #                                                                  N-4  N-3  N-2    N-1
#                     # 3.0.4:
#                     #       INET/inet_error: read errno = 10054, client host = csprog, address = 127.0.0.1 3298, user zotov
#                     #                                                                                 ^     ^     ^      ^
#                     #                                                                                N-4   N-3   N-2   N-1
#                     # 3.0.8 and 4.0.0 RC1:
#                     #       INET/inet_error: read errno = 10054, client host = csprog, address = fe80::fcf1:e33c:e924:969d%16/56887, user = zotov
#                     #       INET/inet_error: read errno = 10054, client host = csprog, address = fe80::fcf1:e33c:e924:969d%16/56883, user = zotov
#               
#               
#                  Checked on WI-V3.0.0.32272 x86 and amd64, OS = Windows XP and 8.1, TCPv4 and TCPv6; fdb version = 1.5, Python 2.7 and 3.4.
#                  Checked 17.02.2018 after adding 2.5.9 to the list of avaliable versions:
#                      2.5.9.27103: OK, 5.547s.
#                      3.0.3.32837: OK, 7.079s.
#                      3.0.4.32912: OK, 6.094s.
#                      4.0.0.800: OK, 7.109s.
#                      4.0.0.890: OK, 6.360s.
#                  ### NB ###
#                  First version of this test was implemented on Windows XP and Python 2.7.8, build 02-jul-2014 win32.
#                  Unfortunatelly, on Python 3.4 + Win 8.1 it is unable to use socket.inet_pton() call -exception raises with text:
#                  "AttributeError: 'module' object has no attribute 'inet_pton'".
#                  For that reason it was decided do NOT use calls of socket.inet_pton() and operate only with remote_address that can be easy
#                  received using built-in FB context variable. User-defined functions 'is_valid_ipv4' and 'is_valid_ipv6' are left here for
#                  possible further usage in some other tests.
#                  
#                  20.02.2021: changed 'platform' attribute to Windows only. Content of firebird.log has no changes on Linux during this test run.
#                  Perhaps, this is temporary and another solution will be found/implemented. Sent letter to dimitr et al, 21.02.2021 08:20.
#                
# tracker_id:   CORE-2493
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table log(ip varchar(255));
    create sequence g;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  from subprocess import Popen
#  import signal
#  import difflib
#  import re
#  import socket
#  import getpass
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  engine = str(db_conn.engine_version)
#  db_conn.close()
#  
#  #-----------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      os.fsync(file_handle.fileno())
#  
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
#  #-------------------------------------------
#  
#  
#  def svc_get_fb_log( engine, f_fb_log ):
#  
#      import subprocess
#  
#      if engine.startswith('2.5'):
#          get_firebird_log_key='action_get_ib_log'
#      else:
#          get_firebird_log_key='action_get_fb_log'
#  
#      subprocess.call([ context['fbsvcmgr_path'],
#                        "localhost:service_mgr",
#                        get_firebird_log_key
#                      ],
#                       stdout=f_fb_log, 
#                       stderr=subprocess.STDOUT
#                     )
#  
#      return
#  
#  #--------------------------------------------
#  
#  # http://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
#  def is_valid_ipv4(address):
#      import socket
#      try:
#          socket.inet_pton(socket.AF_INET, address)
#      except AttributeError:  # no inet_pton here, sorry
#          try:
#              socket.inet_aton(address)
#          except socket.error:
#              return False
#          return address.count('.') == 3
#      except socket.error:  # not a valid address
#          return False
#  
#      return True
#  
#  #--------------------------------------------
#  
#  def is_valid_ipv6(address):
#      import socket
#      try:
#          socket.inet_pton(socket.AF_INET6, address)
#      except socket.error:  # not a valid address
#          return False
#      return True
#  
#  #--------------------------------------------
#  
#  f_fblog_before=open(os.path.join(context['temp_directory'],'tmp_2493_fblog_before.txt'), 'w')
#  
#  svc_get_fb_log( engine, f_fblog_before )
#  
#  f_fblog_before.close()
#  
#  isql_txt='''    insert into log(ip) values( rdb$get_context('SYSTEM','CLIENT_ADDRESS') );
#      commit;
#      select count(i) from (select gen_id(g,1) i from rdb$types a,rdb$types b,rdb$types c,rdb$types d);
#  '''
#  
#  f_sql_txt=open( os.path.join(context['temp_directory'],'tmp_2493_isql.sql'), 'w')
#  f_sql_txt.write(isql_txt)
#  flush_and_close( f_sql_txt )
#  
#  f_sql_log=open(os.path.join(context['temp_directory'],'tmp_2493_isql.log'), 'w' )
#  f_sql_err=open(os.path.join(context['temp_directory'],'tmp_2493_isql.err'), 'w' )
#  
#  p_isql=Popen( [ context['isql_path'], dsn, "-i", f_sql_txt.name ],                           stdout=f_sql_log, stderr=f_sql_err
#                        )
#  time.sleep(3)
#  
#  p_isql.terminate()
#  
#  flush_and_close( f_sql_log )
#  flush_and_close( f_sql_err )
#  
#  f_sql_txt=open(os.path.join(context['temp_directory'],'tmp_2493_isql.sql'), 'w')
#  f_sql_txt.write("set heading off; select iif(gen_id(g,0) = 0, 'Trouble with subprocess: job was not started.', ip) as msg from log; quit;")
#  flush_and_close( f_sql_txt )
#  
#  mon_ip=subprocess.check_output( [ context['isql_path'], dsn, '-i', f_sql_txt.name ]).split()[0]
#  
#  f_fblog_after=open(os.path.join(context['temp_directory'],'tmp_2493_fblog_after.txt'), 'w')
#  
#  svc_get_fb_log( engine, f_fblog_after )
#  
#  flush_and_close( f_fblog_after )
#  
#  oldfb=open(f_fblog_before.name, 'r')
#  newfb=open(f_fblog_after.name, 'r')
#  
#  difftext = ''.join(difflib.unified_diff(
#      oldfb.readlines(), 
#      newfb.readlines()
#    ))
#  oldfb.close()
#  newfb.close()
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_2493_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  inet_msg_words = []
#  logged_err=0
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+') and 'INET/INET_ERROR' in line.upper():
#              # DO NOT include ':' to the list of delimiters! It is involved in IPv6 address:
#              inet_msg_words = line.replace(',',' ').replace('/',' ').replace('=',' ').split()
#              break
#  
#  # Tokens, numerated from zero (NB: leftmost is "PLUS" sign and has index = 0)
#  # ---------------------------------------------------------------------------
#  # + INET inet_error read errno 10054 client host prog1 address 127.0.0.1 4417   user john ------- for IPv4
#  # 0  1       2       3    4      5     6     7     8       9       10      11     12   13
#  # + INET inet_error read errno 10054 client host prog2 address x::y:z:u:v 56831 user mick ------- for IPv6
#  
#  # + INET/inet_error: read errno = 10054, client host = csprog, address = fe80::fcf1:e33c:e924:969d%16/56883, user = zotov
#  # 0       1            2    3       4       5     6       7       8                       9             10    11      12   -->  len() = 13
#  
#  n = len(inet_msg_words)
#  
#  parsing_problem_msg = 'Problem with parsing content of firebird.log'
#  if len(inet_msg_words) == 0:
#      print('%s: message with "inet_error" not found.' % parsing_problem_msg)
#  elif len(inet_msg_words) < 4:
#      print('%s: message with "inet_error" contains less than 4 tokens.' % parsing_problem_msg)
#  else:
#  
#      #print('Fixed data: '+inet_msg_words[4]+' '+inet_msg_words[5]+' '+inet_msg_words[6]+' '+inet_msg_words[7])
#  
#      # http://stackoverflow.com/questions/4271740/how-can-i-use-python-to-get-the-system-hostname
#      
#      # commented 17.02.2017 due to 2.5.9 (no info about remote host there):
#      #if inet_msg_words[8].upper()==socket.gethostname().upper():
#      #    print('Remote host: valid, passed socket.gethostname()')
#      #else:
#      #    print('Invalid host=|'+inet_msg_words[8]+'|')
#  
#      # does not work on Python 3.4! >>> if is_valid_ipv4(inet_msg_words[10]) or is_valid_ipv6(inet_msg_words[10]):
#      if inet_msg_words[n-4] + '/' + inet_msg_words[n-3] == mon_ip:
#          print("String IP/port: valid, equal to 'CLIENT_ADDRESS'")
#      else:
#          print('Invalid IP/port=|'+inet_msg_words[n-4]+'/'+inet_msg_words[n-3]+'| - differ from mon_ip=|'+mon_ip+'|')
#  
#      if inet_msg_words[n-3].isdigit():
#          print('Port value: valid, positive integer.')
#      else:
#          print('Invalid port=|'+inet_msg_words[n-3]+'|')
#  
#      if inet_msg_words[n-1].upper().split('.')[0] == getpass.getuser().upper():
#          # 2.5.9: got 'ZOTOV.-1.-1' ==> must be kust of one word: 'ZOTOV'
#          print('OS user: valid, passed getpass.getuser()')
#      else:
#          print('Invalid OS user=|'+inet_msg_words[n-1]+'|')
#  
#  
#  # Cleanup.
#  ##########
#  time.sleep(1)
#  cleanup( [i.name for i in (f_sql_txt,f_sql_log,f_sql_err,f_fblog_before,f_fblog_after,f_diff_txt) ] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    String IP/port: valid, equal to 'CLIENT_ADDRESS'
    Port value: valid, positive integer.
    OS user: valid, passed getpass.getuser()
  """

@pytest.mark.version('>=2.5.9')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


