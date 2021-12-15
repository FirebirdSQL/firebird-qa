#coding:utf-8
#
# id:           bugs.core_6097
# title:        Connection does not see itself in the MON$ATTACHMENTS when Domain/Username (using SSPI) is 31 bytes long
# decription:
#                   Could not reproduce bug on WI-V3.0.4.33054, discussed this with dimitr and alex.
#               	Problem can appear randomly when some byte in memory contains value not equal to 0x0.
#               	It was decided to implement test that
#               	* adds user with name of 31 octets (15 non-ascii, plus 1 ascii character: "Ковалевский_Олег");
#               	* launches ISQL utility as separate process with trying to connect do test DB using this non-ascii login;
#               	* count record in mon$attachments table that belongs to current attachment. Result must be: 1.
#               	::: NB :::
#               	As of fdb 2.0.1 and fbtest 1.0.7, there is NO ability to run macros runProgram() with specifying non-ascii user name
#               	in its parameters list: errror 'invalid user/password' will raise in this case. The same error will be raised if we
#               	try to launch isql directly in subprocess.call(). For this reason it was decided to create temporary BATCH file (.bat)
#               	that contains necessary command to run isql.exe, i.e. we actually invoke new instance of cmd.exe.
#               	The reason of why 'invalid user/password' raises (in other cases) remains unclear for me.
#               	Checked on:
#               		4.0.0.1564: OK, 3.910s.
#               		4.0.0.1535: OK, 4.052s.
#               		3.0.5.33160: OK, 1.971s.
#               		3.0.5.33152: OK, 3.860s.
#
# tracker_id:   CORE-6097
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import subprocess
#  import time
#  import fdb
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#
#  fb_home = services.connect(host='localhost', user= user_name, password= user_password).get_home_directory()
#
#  sql_txt='''
#      -- fb_home = %s
#      set bail on;
#      set count on;
#      set list on;
#      create or alter user "Ковалевский_Олег" password '123' using plugin Srp;
#      commit;
#      set list on;
#      select sec$user_name, octet_length(trim(sec$user_name)) as octets_in_name from sec$users where sec$user_name = 'Ковалевский_Олег';
#      commit;
#  ''' % (fb_home,)
#
#  f_init_sql=open( os.path.join(context['temp_directory'],'tmp_6097_prepare.sql'), 'w')
#  f_init_sql.write( sql_txt )
#  f_init_sql.close()
#
#  f_init_log=open( os.path.join(context['temp_directory'],'tmp_6097_prepare.log'), 'w')
#
#  subprocess.call([ fb_home+"isql", dsn, "-q", "-ch", "utf8", "-i", f_init_sql.name], stdout=f_init_log, stderr=subprocess.STDOUT)
#  f_init_log.close()
#
#  # does not work, raises 'invalid user/password':
#  #runProgram( fb_home+'isql', [dsn, "-q", "-user", "Ковалевский_Олег", "-pas", "123" ], 'set list on; set count on; select * from mon$attachments where mon$attachment_id = current_connection;')
#
#  f_check_sql=open( os.path.join(context['temp_directory'],'tmp_6097_check.sql'), 'w')
#  #f_check_sql.write( 'set list on; select count(*) as "Can_i_see_myself ?" from mon$attachments where mon$attachment_id = current_connection;' )
#  f_check_sql.write( 'set count on; set list on; select mon$user as who_am_i, left(mon$remote_protocol,3) as mon_protocol, mon$auth_method as mon_auth_method from mon$attachments where mon$attachment_id = current_connection;' )
#  f_check_sql.close()
#
#  f_bat_text='''
#  @echo off
#  chcp 65001 1>nul
#  %s %s -user "Ковалевский_Олег" -pas 123 -ch utf8 -q -i %s
#  ''' % ( fb_home+'isql.exe', dsn, f_check_sql.name )
#  #''' % ( fb_home+'isql.exe', 'localhost:employee', f_check_sql.name )
#
#  f_check_bat=open( os.path.join(context['temp_directory'],'tmp_6097_check.bat'), 'w')
#  f_check_bat.write( f_bat_text )
#  f_check_bat.close()
#
#  f_check_log=open( os.path.join(context['temp_directory'],'tmp_6097_check.log'), 'w')
#  # does not work, raises 'invalid user/password': subprocess.call(["isql", dsn, "-q", "-user", "Ковалевский_Олег", "-pas", "123", "-ch", "utf8", "-i", f_check_sql.name], stdout=f_run_log, stderr=subprocess.STDOUT)
#  subprocess.call([f_check_bat.name], stdout=f_check_log, stderr=subprocess.STDOUT)
#  f_check_log.close()
#
#  # Let redirected output of isql be flushed on disk:
#  time.sleep(1)
#
#  with open( f_init_log.name,'r') as f:
#      for line in f:
#  	    print(line)
#
#  with open( f_check_log.name,'r') as f:
#      for line in f:
#  	    print(line)
#
#  # Cleanup.
#  ##########
#
#  f_list = (f_init_sql, f_init_log, f_check_sql, f_check_bat, f_check_log)
#  for i in range(len(f_list)):
#     if os.path.isfile(f_list[i].name):
#         os.remove(f_list[i].name)
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
	SEC$USER_NAME                   Ковалевский_Олег
	OCTETS_IN_NAME                  31
	Records affected: 1

	WHO_AM_I                        Ковалевский_Олег
	MON_PROTOCOL                    TCP
	MON_AUTH_METHOD                 Srp
	Records affected: 1
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


