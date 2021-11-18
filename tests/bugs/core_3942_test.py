#coding:utf-8
#
# id:           bugs.core_3942
# title:        Restore from gbak backup using service doesn't report an error
# decription:
#                    Checked on:
#                      WI-V2.5.6.26994 SC
#                      WI-V3.0.0.32474 SS/SC/CS
#                      LI-T4.0.0.130 // 11.04.2016
#                      WI-T4.0.0.132 // 12.04.2016
#
# tracker_id:   CORE-3942
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file
from firebird.driver import DatabaseError

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  db_conn.close()
#  fdb='$(DATABASE_LOCATION)bugs.core_3942.fdb'
#  fbk = os.path.join(context['temp_directory'],'tmp.core_3942.fbk')
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,dsn,fbk])
#  print ('Trying to overwrite existing database file using gbak -se...')
#  runProgram('gbak',['-c','-se','localhost:service_mgr','-user',user_name,'-password',user_password,fbk,fdb])
#  print ('Trying to overwrite existing database file using fbsvcmgr...')
#  runProgram('fbsvcmgr',['localhost:service_mgr','user','SYSDBA','password','masterkey','action_restore','dbname',fdb,'bkp_file',fbk])
#  if os.path.isfile(fbk):
#      os.remove(fbk)
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

fbk_file_1 = temp_file('test.fbk')

@pytest.mark.version('>=2.5')
def test_1(act_1: Action, fbk_file_1: Path):
    with act_1.connect_server() as srv:
        srv.database.backup(database=str(act_1.db.db_path), backup=str(fbk_file_1))
        srv.wait()
        # Try overwrite existing database file
        with pytest.raises(DatabaseError,
                           match='atabase .* already exists.  To replace it, use the -REP switch'):
            srv.database.restore(database=str(act_1.db.db_path), backup=str(fbk_file_1))
            srv.wait()


