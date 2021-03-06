#coding:utf-8
#
# id:           bugs.core_2861
# title:        Cannot remove user with dot in login
# decription:   
#                  Since 10.01.2016 this test (for 3.0) is based on totally new algorithm with checking ability of 
#                  normal work with randomly generated logins. These logins consists only of punctuation chars and 
#                  for sure will have at least one dot.
#                  The reason of this replacement was failed results on Classic 3.0 when 'gsec' utility is invoked.
#                  Code for 2.5 was not changed and is preserved (though it was missed for 2.5 before, but it works OK).
#               
#                  See http://web.firebirdsql.org/download/prerelease/results/archive/  for builds: 3.0.0.32266 3.0.0.32268
#               
#                  Correctness of current code was verified by batch scenario, totally about ~1500 iterations was done.
#                  Several samples of logins that were be checked:
#                       ,(/;.>_:%$^`.&<|#?=[~\\*}-{@)
#                       >=[{+%\\.&|~$`(;#._,])}?*@:^!
#                       }^\\*@.)#>|/;&!=~`]<[,?.-:(%.
#               
#                  NOTE: currently we EXCLUDE single and double quotes from random login because of CORE-5072.
#               
#                  This login is handled then by both FBSVCMGR and ISQL utilities:
#                  1) run FBSVCMGR and:
#                     1.1) add user 
#                     1.2) modifying some of its attributes (password, firstname etc).
#                     NOTE! We do *not* run 'fbsvcmgr action_delete_user' because it does not work (at least on build 32268)
#                     ######################################################################################################
#                     COMMAND: fbsvcmgr localhost/3333:service_mgr user sysdba password masterkey action_delete_user dbname C:\\MIX
#               irebird
#               b30\\security3.fdb sec_username john
#                     STDERR:  unexpected item in service parameter block, expected isc_spb_sec_username
#                     (sent letter to Alex, 09-jan-2016 22:34; after getting reply about this issue test can be further changed).
#                  2) run ISQL and:
#                    2.1) drop this user that could not be dropped in FBSVCMGR - see previous section.
#                    2.2) create this login again;
#                    2.3) modifying some of this login attributes;
#                    2.4) drop it finally.
#                    
#                  See also:
#                  CORE-1810 ("Usernames with '.' character"; login 'JOHN.SMITH' is used there).
#                  CORE-3000 (use of unquoted reserved word ADMIN as user name in SQL command).
#                
# tracker_id:   CORE-2861
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('[ ]+', ' '), ('[\t]*', ' '), ('.* Name: .*', ' Name: <name.with.puncts>')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  from subprocess import Popen
#  import string
#  from random import sample, choice
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_name=db_conn.database_name
#  db_conn.close()
#  
#  svc = services.connect(host='localhost')
#  security_db_name = svc.get_security_database_path()  # path+name of security DB
#  svc.close()
#  
#  # Useful links related to this .fbt:
#  # https://docs.python.org/2/library/string.html
#  # http://stackoverflow.com/questions/3854692/generate-password-in-python
#  # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
#  # http://stackoverflow.com/questions/1024049/is-it-pythonic-to-import-inside-functions
#  # http://stackoverflow.com/questions/3095071/in-python-what-happens-when-you-import-inside-of-a-function
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
#  
#  
#  #--------------------------------------------
#  
#  def svc_show_user( f_svc_log, f_svc_err, title_msg, security_db_name, sec_user ):
#  
#    global subprocess
#  
#    f_svc_log.seek(0,2)
#    f_svc_log.write("\\n")
#    f_svc_log.write(title_msg)
#    f_svc_log.write("\\n")
#    f_svc_log.seek(0,2)
#  
#    subprocess.call( [ context['fbsvcmgr_path'],
#                      "localhost:service_mgr",
#                      "action_display_user_adm",
#                      "dbname",         security_db_name,
#                      "sec_username",   sec_user,
#                     ],
#                     stdout=f_svc_log, stderr=f_svc_err
#                   )
#    return
#  
#  #--------------------------------------------
#  
#  f_svc_log=open( os.path.join(context['temp_directory'],'tmp_2861_fbsvc.log'), 'w')
#  f_svc_err=open( os.path.join(context['temp_directory'],'tmp_2861_fbsvc.err'), 'w')
#  
#  chars = string.punctuation 
#  
#  # + string.digits 
#  #string.letters + string.digits
#  # do NOT: chars = string.printable -- it includes whitespaces, i.e. LF etc!
#  
#  # NB: maximal part of user name that is displayed in fbsvcmgr action_display_user is only 28 chars.
#  # We build user name as two parts delimited by dot, so max. length of these parts is bound to 13,
#  # otherwise total length of user name will be 14+1+14 = 29 and we'll get mismatch on expected stdout.
#  
#  
#  '''
#  length = 13
#  dotted_user=''.join(sample(chars,length)).replace('"','.').replace("'",'.')
#  dotted_user=dotted_user+'.'+''.join(sample(chars,length))
#  dotted_user=dotted_user.replace('"','""').replace("'","''")
#  '''
#  
#  length = 28
#  dotted_user=''.join(sample(chars,length)).replace('"','.').replace("'",'.')
#  quoted_user='"'+dotted_user+'"'
#  
#  f_svc_log.write("Try to add user with name: "+quoted_user)
#  f_svc_log.write("\\n")
#  f_svc_log.seek(0,2)
#  
#  subprocess.call( [ context['fbsvcmgr_path'],
#                      "localhost:service_mgr",
#                      "action_add_user",
#                      "dbname",       security_db_name,
#                      "sec_username", quoted_user,
#                      "sec_password", "foobarkey",
#                      "sec_admin",    "1"
#                    ],
#                    stdout=f_svc_log, stderr=f_svc_err
#                 )
#  
#  svc_show_user( f_svc_log, f_svc_err, "Try to display user after adding.", security_db_name, quoted_user )
#  
#  f_svc_log.seek(0,2)
#  f_svc_log.write("\\n")
#  f_svc_log.write("Try to modify user: change password and some attributes.")
#  f_svc_log.write("\\n")
#  f_svc_log.seek(0,2)
#  
#  subprocess.call( [ context['fbsvcmgr_path'],
#                      "localhost:service_mgr",
#                      "action_modify_user",
#                      "dbname",         security_db_name,
#                      "sec_username",   quoted_user,
#                      "sec_password",   "BSabbath",
#                      "sec_firstname",  "Ozzy",
#                      "sec_middlename", "The Terrible",
#                      "sec_lastname",   "Osbourne",
#                      "sec_admin",      "0"
#                    ],
#                    stdout=f_svc_log, stderr=f_svc_err
#                 )
#  
#  svc_show_user( f_svc_log, f_svc_err, "Try to display user after modifying.", security_db_name, quoted_user )
#  
#  f_svc_log.seek(0,2)
#  f_svc_log.write("\\n")
#  f_svc_log.write("All done.")
#  f_svc_log.write("\\n")
#  
#  flush_and_close( f_svc_log )
#  flush_and_close( f_svc_err )
#  
#  #####################################
#  
#  # Now we drop user (using ISQL - fbsvcmgr currently does not work)
#  # and then create + modify + drop him again by ISQL.
#  
#  
#  isql_txt='''---- %s
#      set list on;
#      --set echo on;
#      create or alter view v_sec as select sec$user_name, sec$first_name, sec$middle_name, sec$last_name, sec$admin
#      from sec$users
#      where upper(sec$user_name)=upper('%s');
#      commit;
#  
#      -- select * from v_sec; commit; -- ==> FOO.RIO.BAR, in UPPER case (left after fbsvcmgr add_user)
#  
#      drop user %s;
#      commit;
#  
#      select 'Try to add user with name: ' || '%s' as isql_msg from rdb$database;
#  
#      create or alter user %s password '123' grant admin role;
#      commit;
#  
#      select 'Try to display user after adding.' as isql_msg from rdb$database;
#  
#      select * from v_sec;
#      commit;
#  
#      select 'Try to modify user: change password and some attributes.' as isql_msg from rdb$database;
#  
#      alter user %s
#          password 'Zeppelin'
#          firstname 'John'
#          middlename 'Bonzo The Beast'
#          lastname 'Bonham'
#          revoke admin role
#      ;
#      commit;
#  
#      select 'Try to display user after modifying.' as isql_msg from rdb$database;
#      select * from v_sec;
#      commit;
#  
#      select 'Try to drop user.' as isql_msg from rdb$database;
#      drop user %s;
#      commit;
#      select 'All done.' as isql_msg from rdb$database;
#  ''' % (dotted_user, dotted_user, quoted_user.upper(), dotted_user, quoted_user, quoted_user, quoted_user )
#  
#  f_sql_txt=open( os.path.join(context['temp_directory'],'tmp_2861_isql.sql'), 'w')
#  f_sql_txt.write(isql_txt)
#  flush_and_close( f_sql_txt )
#  
#  f_sql_log=open( os.path.join(context['temp_directory'],'tmp_2861_isql.log'), 'w')
#  f_sql_err=open( os.path.join(context['temp_directory'],'tmp_2861_isql.err'), 'w')
#  
#  subprocess.call( [ context['isql_path'], dsn, "-i",   f_sql_txt.name ],
#                   stdout=f_sql_log, stderr=f_sql_err
#                 )
#  
#  flush_and_close( f_sql_log )
#  flush_and_close( f_sql_err )
#  
#  with open( f_svc_log.name,'r') as f:
#    l = [l for l in f.readlines() if l.strip()]
#  
#  for line in l:
#     print("SVC STDOUT: "+line.replace(dotted_user.upper(),"<name.with.puncts>") )
#  
#  with open( f_svc_err.name,'r') as f:
#    l = [l for l in f.readlines() if l.strip()]
#  
#  for line in l:
#     print("SVC STDERR: "+line+", user: "+dotted_user)
#  
#  with open( f_sql_log.name,'r') as f:
#    l = [l for l in f.readlines() if l.strip()]
#  
#  for line in l:
#     print("SQL STDOUT: "+line.replace(dotted_user,"<name.with.puncts>"))
#  
#  with open( f_sql_err.name,'r') as f:
#    l = [l for l in f.readlines() if l.strip()]
#  
#  for line in l:
#     print("SQL STDERR: "+line+", user: "+dotted_user)
#  
#  
#  # Cleanup.
#  ##########
#  
#  time.sleep(1)
#  cleanup( [i.name for i in (f_svc_log,f_svc_err,f_sql_log,f_sql_err,f_sql_txt)] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SVC STDOUT: Try to add user with name: "<name.with.puncts>"
    SVC STDOUT: Try to display user after adding.
    SVC STDOUT: Login                        Full name                                 uid  gid adm
    SVC STDOUT: <name.with.puncts>                                                              0    0 yes
    SVC STDOUT: Try to modify user: change password and some attributes.
    SVC STDOUT: Try to display user after modifying.
    SVC STDOUT: Login                        Full name                                 uid  gid adm
    SVC STDOUT: <name.with.puncts>                  Ozzy The Terrible Osbourne                  0    0  no
    SVC STDOUT: All done.
    SQL STDOUT: ISQL_MSG                        Try to add user with name: <name.with.puncts>
    SQL STDOUT: ISQL_MSG                        Try to display user after adding.
    SQL STDOUT: SEC$USER_NAME                   <name.with.puncts>
    SQL STDOUT: SEC$FIRST_NAME                  <null>
    SQL STDOUT: SEC$MIDDLE_NAME        		<null>
    SQL STDOUT: SEC$LAST_NAME                   <null>
    SQL STDOUT: SEC$ADMIN                       <true>
    SQL STDOUT: ISQL_MSG                        Try to modify user: change password and some attributes.
    SQL STDOUT: ISQL_MSG                        Try to display user after modifying.
    SQL STDOUT: SEC$USER_NAME                   <name.with.puncts>
    SQL STDOUT: SEC$FIRST_NAME                  John
    SQL STDOUT: SEC$MIDDLE_NAME                 Bonzo The Beast
    SQL STDOUT: SEC$LAST_NAME                   Bonham
    SQL STDOUT: SEC$ADMIN                       <false>
    SQL STDOUT: ISQL_MSG                        Try to drop user.
    SQL STDOUT: ISQL_MSG                        All done.
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


