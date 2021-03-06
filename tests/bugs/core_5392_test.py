#coding:utf-8
#
# id:           bugs.core_5392
# title:        BUGCHECK 179 (decompression overran buffer) or unexpected lock conflict may happen during record versions backout
# decription:   
#                  NOTE: bug can be reproduced only in SuperServer arch.
#               
#                  We determine FB arch, and if it is SuperServer then change FW to OFF, add rows into table and 
#                  perform statements that should raise internal FB CC.
#                  If no errors occures then ISQL log should contain number of affected rows.
#                  If internal FB CC will occur again then control will be returned to fbtest after ~2 minutes.
#                  
#                  For SS test lasts about 40 seconds, for SC/CS it should pass instantly because we SKIP entire test
#                  for both SC and CS architectures and just print 'OK' for matching expected_stdout.
#               
#                  Confirmed bug on  WI-T4.0.0.462, minimal number of rows for reproducing is ~98000.
#                  Checked on WI-V3.0.2.32643,  WI-T4.0.0.463 - works fine.
#                  -------
#                  01-feb-2017: confirmed bugcheck on 2.5.7.27030 (only with WF = OFF), fix on 2.5.7.27038.
#                  Changed min-version to 2.5.7.
#                
# tracker_id:   CORE-5392
# min_versions: ['2.5.7']
# versions:     2.5.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.7
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
#  #from subprocess import Popen
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
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
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  def get_fb_arch(a_dsn):
#     try:
#        con1 = fdb.connect(dsn = a_dsn)
#        con2 = fdb.connect(dsn = a_dsn)
#  
#        cur1 = con1.cursor()
#  
#        sql=(
#               "select count(distinct a.mon$server_pid), min(a.mon$remote_protocol), max(iif(a.mon$remote_protocol is null,1,0))"
#              +" from mon$attachments a"
#              +" where a.mon$attachment_id in (%s, %s) or upper(a.mon$user) = upper('%s')"
#              % (con1.attachment_id, con2.attachment_id, 'cache writer')
#            )
#  
#        cur1.execute(sql)
#        for r in cur1.fetchall():
#            server_cnt=r[0]
#            server_pro=r[1]
#            cache_wrtr=r[2]
#  
#        if server_pro == None:
#            fba='Embedded'
#        elif cache_wrtr == 1:
#            fba='SS'
#        elif server_cnt == 2:
#            fba='CS'
#        else:
#  
#            f1=con1.db_info(fdb.isc_info_fetches)
#            
#            cur2=con2.cursor()
#            cur2.execute('select 1 from rdb$database')
#            for r in cur2.fetchall():
#               pass
#  
#            f2=con1.db_info(fdb.isc_info_fetches)
#  
#            fba = 'SC' if f1 ==f2 else 'SS'
#  
#        return fba
#  
#     finally:
#        con1.close()
#        con2.close()
#  
#  #--------------------------------------------
#  
#  fb_arch= get_fb_arch(dsn)
#  rows_cnt=100000
#  
#  if fb_arch == 'SS':
#  
#      dbname=db_conn.database_name
#      db_conn.close()
#  
#      # NB: do _not_ remove changing of FW to OFF in 2.5.7 (Ivan said that FW on 2.5.6 was ON, see 15/Dec/16 01:07 PM).
#      # Bucgcheck is reproduced on 2.5.7.27030 only when FW = OFF.
#      fn_nul = open(os.devnull, 'w')
#      subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr", 
#                        "action_properties", "dbname", dbname, 
#                        "prp_write_mode", "prp_wm_async" ],
#                       stdout = fn_nul,
#                       stderr = subprocess.STDOUT
#                     )
#      fn_nul.close()
#  
#      sql_chk=    '''
#          create domain dm_longutf as varchar(8000) character set utf8;
#          recreate table test (id int not null, a int);
#          commit;
#  
#          set term ^;
#          execute block as
#            declare i int;
#            declare n int = %(rows_cnt)s; -- (4.0 SS, page_size 8k: threshold is ~98000 records)
#          begin
#              while (n>0) do insert into test(id, a) values(:n, :n) returning :n-1 into n;
#          end
#          ^
#          set term ;^
#          commit;
#          alter table test add constraint pk_test primary key (id) using descending index pk_test_desc;
#          commit;
#  
#          alter table test add b dm_longutf default '' not null;
#          commit;
#  
#          update test set a=2;
#          rollback;
#  
#          set count on;
#          -- Following UPDATE statement leads to:
#          -- 1) on 3.0: decompression overran buffer (179), file: sqz.cpp line: 282
#          -- 2) on 2.5.7.27030: decompression overran buffer (179), file: sqz.cpp line: 228
#          -- Then FB waits (or is doing?) somewhat about 2 minutes abd after this 
#          -- control is returned to fbtest.
#          update test set a=3; 
#          commit;
#      ''' % locals()
#  
#      f_sql_cmd=open(os.path.join(context['temp_directory'],'tmp_core_5392.sql'), 'w')
#      f_sql_cmd.write(sql_chk)
#      flush_and_close( f_sql_cmd )
#  
#      f_sql_log=open(os.path.join(context['temp_directory'],'tmp_core_5392.log'),'w')
#      f_sql_err=open(os.path.join(context['temp_directory'],'tmp_core_5392.err'),'w')
#  
#      subprocess.call([context['isql_path'], dsn, "-i", f_sql_cmd.name],stdout=f_sql_log, stderr=f_sql_err)
#  
#      flush_and_close( f_sql_log )
#      flush_and_close( f_sql_err )
#  
#      # This should contain message about affected <rows_cnt> rows:
#      #####################
#      with open( f_sql_log.name,'r') as f:
#          for line in f:
#              if 'affected: '+str(rows_cnt) in line:
#                  print('OK')
#  
#      # This should be empty:
#      #######################
#      with open( f_sql_err.name,'r') as f:
#          for line in f:
#              if line.strip():
#                  print('UNEXPECTED ERROR: '+line.upper())
#      # Cleanup
#      #########
#      time.sleep(1)
#      cleanup( (f_sql_cmd, f_sql_log, f_sql_err) )
#      
#  else:
#      # FB arch is NOT SuperServer: test should not run at all because its subject relates only to SS.
#      # (see leter from dimitr, 06-dec-2016 08:37, about races between GC and working DML thread).
#      print('OK')
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    OK
  """

@pytest.mark.version('>=2.5.7')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


