#coding:utf-8
#
# id:           bugs.core_2208
# title:        New gbak option to ignore specific tables data during the backup
# decription:
#                  We create four tables with ascii and one with non-ascii (cyrillic) names.
#                  Each table has one row.
#                  Then we check that one may to:
#                  1) skip BACKUP data of some tables
#                  2) skip RESTORE data for same tables.
#                  All cases are checked by call 'fbsvcmgr ... bkp_skip_data <pattern>',
#                  where <pattern> string matches several tables (i.e. we use SIMILAR_TO ability).
#
#                  WARNING!
#                  It was found that there is NO ability (in fbtest only! not in command interpreter)
#                  to skip data from backup for table with non-ascii name, neither if we specify its name
#                  as literal nor via pattern. For that reason one of checks currently is commented
#                  (see below block titled as: `Run-3: try to skip BACKUP of data for table "опечатка"`).
#
#                  Checked on WI-V3.0.2.32644, WI-T4.0.0.469.
#
# tracker_id:   CORE-2208
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from io import BytesIO
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file
from firebird.driver import SrvRestoreFlag

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
     recreate table test_01(id char(1));
     recreate table test_02(id char(1));
     recreate table test_0a(id char(1));
     recreate table test_0b(id char(1));

     recreate table "опечатка"(id char(1));
     commit;

     insert into test_01(id) values('1');
     insert into test_02(id) values('2');
     insert into test_0a(id) values('3');
     insert into test_0b(id) values('4');
     insert into "опечатка"(id) values('ы');
     commit;
     --  similar to '(о|а)(п|ч)(е|и)(п|ч)(а|я)(т|д)(к|г)(а|о)';
     recreate view v_check as
        select 'test_01' as msg, t.id
        from rdb$database left join test_01 t on 1=1
        union all
        select 'test_02' as msg, t.id
        from rdb$database left join test_02 t on 1=1
        union all
        select 'test_0a' as msg, t.id
        from rdb$database left join test_0a t on 1=1
        union all
        select 'test_0b' as msg, t.id
        from rdb$database left join test_0b t on 1=1
        union all
        select 'опечатка' as msg, t.id
        from rdb$database left join "опечатка" t on 1=1
      ;
  """

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import subprocess
#  import time
#  from subprocess import Popen
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  # Obtain engine version:
#  engine = str(db_conn.engine_version) # convert to text because 'float' object has no attribute 'startswith'
#
#  db_conn.close()
#
#  thisdb='$(DATABASE_LOCATION)bugs.core_2208.fdb'
#  tmpbkp='$(DATABASE_LOCATION)bugs.core_2208_fbk.tmp'
#  tmpres='$(DATABASE_LOCATION)bugs.core_2208_new.tmp'
#
#  f_run_sql=open( os.path.join(context['temp_directory'],'tmp_check_2208.sql'), 'w')
#  f_run_sql.write('set list on; set count on; select * from v_check;')
#  f_run_sql.close()
#
#  f_svc_log=open( os.path.join(context['temp_directory'],'tmp_svc_2208.log'), 'w')
#  f_svc_err=open( os.path.join(context['temp_directory'],'tmp_svc_2208.err'), 'w')
#
#  # Run-1: try to skip BACKUP of data for tables 'test_0a' and 'test_0b'.
#  ###########################
#  subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr','action_backup',
#                     'dbname', thisdb, 'bkp_file', tmpbkp,
#                     'bkp_skip_data', 'test_0[[:alpha:]]'
#                   ],
#                   stdout=f_svc_log,stderr=f_svc_err
#                 )
#  subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr','action_restore',
#                     'bkp_file', tmpbkp, 'dbname', tmpres,
#                     'res_replace'
#                   ],
#                   stdout=f_svc_log,stderr=f_svc_err
#                 )
#
#
#  f_run1_log=open( os.path.join(context['temp_directory'],'tmp_run1_2208.log'), 'w')
#  subprocess.call( [ context['isql_path'], 'localhost:'+tmpres,'-q','-ch','utf8', '-i', f_run_sql.name],stdout=f_run1_log,stderr=subprocess.STDOUT )
#  f_run1_log.close()
#
#
#  # Run-2: try to skip RESTORE of data for tables 'test_01' and 'test_02'.
#  ###########################
#  subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr','action_backup',
#                     'dbname', thisdb, 'bkp_file', tmpbkp,
#                     'bkp_skip_data', 'test_0[[:digit:]]'
#                   ],
#                   stdout=f_svc_log,stderr=f_svc_err
#                 )
#  subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr','action_restore',
#                     'bkp_file', tmpbkp, 'dbname', tmpres,
#                     'res_replace'
#                   ],
#                   stdout=f_svc_log,stderr=f_svc_err
#                 )
#
#  f_run2_log=open( os.path.join(context['temp_directory'],'tmp_run2_2208.log'), 'w')
#  subprocess.call( [ context['isql_path'], 'localhost:'+tmpres,'-q','-ch','utf8', '-i', f_run_sql.name],stdout=f_run2_log,stderr=subprocess.STDOUT )
#  f_run2_log.close()
#
#  ########################################
#
#  '''
#      DEFERRED! IT SEEMS THAT WRONG PATTERN IS PASSED FROM FBTEST TO FBSVCMGR WHEN USE NON-ASCII TABLE NAME!
#
#      CAN NOT BE REPRODUCED IN CMD.EXE (chcp 65001):
#      ==============================================
#
#      Script for isql (do not forget to make chcp 65001 before run it):
#      ===
#      set names utf8;
#      shell del C:\\MIX\\firebird\\QA\\fbt-repo\\tmp\\c2208w.fdb 2>nul;
#      create database 'localhost:C:\\MIX\\firebird\\QA\\fbt-repo\\tmp\\c2208w.fdb' default character set utf8;
#      recreate table "опечатка"(id char(1));
#      insert into "опечатка"(id) values('ы');
#      commit;
#      ===
#
#      fbsvcmgr localhost:service_mgr action_backup
#          dbname C:\\MIX\\firebird\\QA\\fbt-repo\\tmp\\C2208W.FDB
#          bkp_file C:\\MIX\\firebird\\QA\\fbt-repo\\tmp\\C2208W.fbk
#          -bkp_skip_data "(о|а)(п|ч)(е|и)(п|ч)(а|я)(т|д)(к|г)(о|а)"
#
#      gbak -rep C:\\MIX\\firebird\\QA\\fbt-repo\\tmp\\C2208W.fbk localhost:C:\\MIX\\firebird\\QA\\fbt-repo\\tmp\\C2208W2.FDB
#
#      echo show table; set list on; set count on; select * from "опечатка";|isql /:C:\\MIX\\firebird\\QA\\fbt-repo\\tmp\\C2208W2.FDB -ch utf8
#
#      опечатка
#      Records affected: 0
#
#      # Run-3: try to skip BACKUP of data for table "опечатка".
#      ###########################
#      # 'bkp_skip_data', '"(о|а)(п|ч)(е|и)(п|ч)(а|я)(т|д)(к|г)(а|о)"'
#      subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr','action_backup',
#                         'dbname', thisdb, 'bkp_file', tmpbkp,
#                         'bkp_skip_data', '%о%'
#                       ],
#                       stdout=f_svc_log,stderr=f_svc_err
#                     )
#      subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr','action_restore',
#                         'bkp_file', tmpbkp, 'dbname', tmpres,
#                         'res_replace'
#                       ],
#                       stdout=f_svc_log,stderr=f_svc_err
#                     )
#
#      f_run3_log=open( os.path.join(context['temp_directory'],'tmp_run3_2208.log'), 'w')
#      subprocess.call( [ context['isql_path'], 'localhost:'+tmpres,'-q','-ch','utf8', '-i', f_run_sql.name],stdout=f_run3_log,stderr=subprocess.STDOUT )
#      f_run3_log.close()
#  '''
#
#  f_svc_log.close()
#  f_svc_err.close()
#
#  # Should be EMPTY:
#  with open( f_svc_err.name,'r') as f:
#    for line in f:
#      if line.split():
#         print('fbsvcmgr(2) unexpected STDERR: '+line.upper() )
#  f.close()
#
#
#  with open( f_run1_log.name,'r') as f:
#    for line in f:
#      if line.split():
#        print('run-1: ' + line)
#  f.close()
#
#  with open( f_run2_log.name,'r') as f:
#    for line in f:
#      if line.split():
#        print('run-2: ' + line)
#  f.close()
#
#  # CLEANUP
#  #########
#  f_list=(f_svc_log, f_svc_err,f_run_sql,f_run1_log,f_run2_log)
#  for i in range(len(f_list)):
#     if os.path.isfile(f_list[i].name):
#         os.remove(f_list[i].name)
#
#  if os.path.isfile(tmpbkp):
#       os.remove(tmpbkp)
#  if os.path.isfile(tmpres):
#       os.remove(tmpres)
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1_a = """
MSG                             test_01
ID                              1
MSG                             test_02
ID                              2
MSG                             test_0a
ID                              <null>
MSG                             test_0b
ID                              <null>
MSG                             опечатка
ID                              ы
Records affected: 5
"""

expected_stdout_1_b = """
MSG                             test_01
ID                              <null>
MSG                             test_02
ID                              <null>
MSG                             test_0a
ID                              3
MSG                             test_0b
ID                              4
MSG                             опечатка
ID                              ы
Records affected: 5
"""

expected_stdout_1_c = """
MSG                             test_01
ID                              1
MSG                             test_02
ID                              2
MSG                             test_0a
ID                              3
MSG                             test_0b
ID                              4
MSG                             опечатка
ID                              <null>
Records affected: 5
"""

# We need additional test database for restore
file_1 = temp_file('extra-test.fdb')

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, file_1: Path):
    check_script = 'set list on; set count on; select * from v_check;'
    if file_1.is_file():
        file_1.unlink()
    with act_1.connect_server() as srv:
        backup = BytesIO()
        # Run-1: try to skip BACKUP of data for tables 'test_0a' and 'test_0b'.
        srv.database.local_backup(database=str(act_1.db.db_path), backup_stream=backup,
                                  skip_data='test_0[[:alpha:]]')
        backup.seek(0)
        srv.database.local_restore(backup_stream=backup, database=str(file_1))
        # check
        act_1.expected_stdout = expected_stdout_1_a
        act_1.isql(switches=['-user', act_1.db.user,
                             '-password', act_1.db.password,
                             str(file_1)], input=check_script, connect_db=False)
        assert act_1.clean_stdout == act_1.clean_expected_stdout
        # Run-2: try to skip RESTORE of data for tables 'test_01' and 'test_02'.
        if file_1.is_file():
            file_1.unlink()
        backup.close()
        backup = BytesIO()
        srv.database.local_backup(database=str(act_1.db.db_path), backup_stream=backup)
        backup.seek(0)
        srv.database.local_restore(backup_stream=backup, database=str(file_1),
                                   skip_data='test_0[[:digit:]]')
        # check
        act_1.reset()
        act_1.expected_stdout = expected_stdout_1_b
        act_1.isql(switches=['-user', act_1.db.user,
                             '-password', act_1.db.password,
                             str(file_1)], input=check_script, connect_db=False)
        assert act_1.clean_stdout == act_1.clean_expected_stdout
        # Run-3: try to skip BACKUP of data for table "опечатка".
        srv.encoding = 'utf8'
        if file_1.is_file():
            file_1.unlink()
        backup.close()
        backup = BytesIO()
        srv.database.local_backup(database=str(act_1.db.db_path), backup_stream=backup,
                                  skip_data='(о|а)(п|ч)(е|и)(п|ч)(а|я)(т|д)(к|г)(о|а)')
        backup.seek(0)
        srv.database.local_restore(backup_stream=backup, database=str(file_1))
        # check
        act_1.reset()
        act_1.expected_stdout = expected_stdout_1_c
        act_1.isql(switches=['-user', act_1.db.user,
                             '-password', act_1.db.password,
                             str(file_1)], input=check_script, connect_db=False)
