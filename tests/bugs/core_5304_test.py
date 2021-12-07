#coding:utf-8
#
# id:           bugs.core_5304
# title:        Regression: Can not restore database with table contains field CHAR(n) and UTF8 character set
# decription:
#                  We make initial DDL and DML using ISQL with connection charset = UTF8, and then run b/r.
#                  Ouput of restore is filtered so that only lines with 'ERROR' word can be displayed.
#                  This output should be EMPTY (i.e. no errors should occur).
#
#                  Confirmed on WI-T4.0.0.258, got:
#                    gbak: ERROR:arithmetic exception, numeric overflow, or string truncation
#                    gbak: ERROR:    string right truncation
#                    gbak: ERROR:    expected length 10, actual 40
#                    gbak: ERROR:    gds_$send failed
#                    gbak: ERROR:    Exiting before completion due to errors
#
#                  All works fine on WI-T4.0.0.313.
#
# tracker_id:   CORE-5304
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 4.0
# resources: None

#substitutions_1 = [('^((?!ERROR).)*$', '')]
substitutions_1 = []

init_script_1 = """
    recreate table test(c char(10));
    commit;
    insert into test values(null);
    commit;
"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#  sql='''
#      recreate table test(c char(10));
#      commit;
#      insert into test values(null);
#      commit;
#  '''
#  runProgram('isql',['-ch','UTF8',dsn],sql)
#
#  tmpfbk = os.path.join(context['temp_directory'],'tmp_core_5304.fbk')
#  tmpres = os.path.join(context['temp_directory'],'tmp_core_5304.fdb')
#
#  runProgram('gbak',['-b',dsn,tmpfbk])
#  runProgram('gbak',['-c','-v','-se','localhost:service_mgr',tmpfbk,tmpres])
#
#  f_list=[tmpfbk,tmpres]
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i]):
#          os.remove(f_list[i])
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

fbk_file = temp_file('tmp_core_5304.fbk')
fdb_file = temp_file('tmp_core_5304.fdb')

@pytest.mark.version('>=4.0')
def test_1(act_1: Action, fbk_file: Path, fdb_file: Path):
    with act_1.connect_server() as srv:
        srv.database.backup(database=act_1.db.db_path, backup=fbk_file)
        srv.wait()
        srv.database.restore(backup=fbk_file, database=fdb_file)
        srv.wait()


