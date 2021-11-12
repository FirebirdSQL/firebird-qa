#coding:utf-8
#
# id:           bugs.core_1865
# title:        BLR error on restore database with computed by Field
# decription:
#                   Confirmed bug on WI-V2.0.0.12724: it was unable to restore DB with "-o" command switch ("-one_at_a_time"):
#                   got errors that are specified in the ticket.
#                   No errors on WI-V2.1.0.17798, and also on:
#                       2.5.9.27107: OK, 1.953s.
#                       3.0.4.32924: OK, 5.281s.
#                       4.0.0.918: OK, 4.078s.
#                   NB-1: old versions of FB did restore with redirection all messages to STDERR, w/o STDOUT. For this reason we store
#                   all output to file and then check whether this file contains at least one line with phrase "ERROR:".
#                   NB-2: could _NOT_ reproduce without use "-o" command switch!
#
# tracker_id:   CORE-1865
# min_versions: ['2.0.0']
# versions:     2.0
# qmid:         None

import pytest
from io import BytesIO
from firebird.qa import db_factory, python_act, Action
from firebird.driver import SrvRestoreFlag

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """
create table tmain(id int);
create table tdetl( id int, pid int, cost numeric(12,2) );
alter table tmain
   add dsum2 computed by ( (select sum(cost) from tdetl d where d.pid = tmain.id) ) ;
commit;
"""

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
#  db_conn.close()
#
#  sql_ddl='''
#      create table tmain(id int);
#      create table tdetl( id int, pid int, cost numeric(12,2) );
#      alter table tmain
#          add dsum2 computed by ( (select sum(cost) from tdetl d where d.pid = tmain.id) )
#      ;
#      commit;
#  '''
#  runProgram('isql', [ dsn, '-q' ], sql_ddl)
#
#  tmpfbk='$(DATABASE_LOCATION)'+'core_1865.fbk'
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_check_1865.fdb'
#
#  runProgram( 'gbak', [ '-b', dsn, tmpfbk ] )
#
#  f_restore_log=open( os.path.join(context['temp_directory'],'tmp_check_1865.log'), 'w')
#  subprocess.call( [ context['gbak_path'],  '-rep', '-o', '-v',  tmpfbk, 'localhost:' + tmpfdb],  stdout = f_restore_log, stderr=subprocess.STDOUT)
#  f_restore_log.close()
#  time.sleep(1)
#
#  # should be empty:
#  ##################
#  with open( f_restore_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              if  'ERROR:'.lower() in line.lower():
#                  print('UNEXPECTED ERROR ON RESTORE: '+line)
#
#  os.remove(f_restore_log.name)
#  os.remove(tmpfdb)
#  os.remove(tmpfbk)
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    backup = BytesIO()
    with act_1.connect_server() as srv:
        srv.database.local_backup(database=str(act_1.db.db_path), backup_stream=backup)
        backup.seek(0)
        # test fails if restore raises an exception
        srv.database.local_restore(backup_stream=backup, database=str(act_1.db.db_path),
                                   flags=SrvRestoreFlag.ONE_AT_A_TIME | SrvRestoreFlag.REPLACE)

