#coding:utf-8
#
# id:           bugs.core_4218
# title:        Add database owner to mon$database
# decription:
# tracker_id:   CORE-4218
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, user_factory, User, temp_file

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import sys
#  import subprocess
#  import time
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  #db_check=db_conn.database_name
#  db_conn.close()
#
#  create_user_ddl='''
#      create or alter user TMP_U4218 password '123' revoke admin role;
#      grant create database to user TMP_U4218;
#  '''
#
#  runProgram('isql',[dsn,'-q'],create_user_ddl)
#
#  db_check = os.path.join(context['temp_directory'],'tmp_check_4218.fdb')
#  if os.path.isfile(db_check):
#      os.remove(db_check)
#
#  create_db_sql='''
#      create database 'localhost:%(db_check)s' user 'TMP_U4218' password '123';
#      set list on;
#      select current_user as who_am_i, mon$owner as who_is_owner from mon$database;
#      commit;
#      connect 'localhost:%(db_check)s';
#      select current_user as who_am_i, mon$owner as who_is_owner from mon$database;
#      commit;
#      drop user TMP_U4218;
#      commit;
#      revoke create database from user TMP_U4218;
#      commit;
#      drop database;
#      quit;
#  ''' % locals()
#
#  sqlddl=open( os.path.join(context['temp_directory'],'tmp_create_db_4218.sql'), 'w')
#  sqlddl.write(create_db_sql)
#  sqlddl.close()
#
#  sqllog=open( os.path.join(context['temp_directory'],'tmp_create_db_4218.log'), 'w')
#  subprocess.call([ context['isql_path'], "-q", "-i", sqlddl.name],stdout=sqllog, stderr=subprocess.STDOUT)
#  sqllog.close()
#
#  with open(sqllog.name) as f:
#    print( f.read() )
#
#  time.sleep(1)
#
#  f_list=[sqlddl, sqllog]
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i].name):
#          os.remove(f_list[i].name)
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        TMP_U4218
    WHO_IS_OWNER                    TMP_U4218
    WHO_AM_I                        SYSDBA
    WHO_IS_OWNER                    TMP_U4218
"""

test_user_1: User = user_factory(name='TMP_U4218', password='123')

test_db_1 = temp_file('owner-db.fdb')

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, test_user_1: User, test_db_1: Path):
    with act_1.db.connect() as con:
        c = con.cursor()
        c.execute('grant create database to user TMP_U4218')
        con.commit()
    test_script_1 = f"""
    create database 'localhost:{str(test_db_1)}' user 'TMP_U4218' password '123';
    set list on;
    select current_user as who_am_i, mon$owner as who_is_owner from mon$database;
    commit;
    connect 'localhost:{str(test_db_1)}';
    select current_user as who_am_i, mon$owner as who_is_owner from mon$database;
    commit;
    drop database;
    quit;
    """
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=['-q'], input=test_script_1)
    assert act_1.clean_stdout == act_1.clean_expected_stdout
