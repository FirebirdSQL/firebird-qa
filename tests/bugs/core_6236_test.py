#coding:utf-8
#
# id:           bugs.core_6236
# title:        RDB$TIME_ZONE_UTIL package has wrong privilege for PUBLIC
# decription:
#                   Thanks Adriano for suggestion about this test implementation.
#                   We create non-privileged user ('tmp$c6236') and do connect of him
#                   with trying to use package function rdb$time_zone_util.database_version().
#                   It must pass without any errors (result of call no matter).
#
#                   Confirmed exception on 4.0.0.1714: no permission for EXECUTE access to PACKAGE RDB$TIME_ZONE_UTIL
#                   Checked on 4.0.0.1740 SS: 1.400s - works fine.
#                   ::: NB :::
#                   Command 'SHOW GRANTS' does not display privileges on system objects thus we do not use it here.
#
# tracker_id:   CORE-6236
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action, user_factory, User

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import inspect
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.execute_immediate("create or alter user tmp$c6236 password '123'")
#  db_conn.commit()
#
#  con = fdb.connect( dsn = dsn, user = 'tmp$c6236', password ='123' )
#  cur = con.cursor()
#  try:
#      cur.execute('select rdb$time_zone_util.database_version() is not null as db_vers_defined from rdb$database')
#      hdr=cur.description
#      for r in cur:
#          for i in range(0,len(hdr)):
#              print( hdr[i][0],':', r[i] )
#  except Exception as e:
#      print('Unexpected exception in ', inspect.stack()[0][3], ': ', sys.exc_info()[0])
#      print(e)
#
#  cur.close()
#  con.close()
#
#  db_conn.execute_immediate("drop user tmp$c6236")
#  db_conn.commit()
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    DB_VERS_DEFINED                 True
"""

test_user = user_factory('db_1', name='tmp$c6236', password='123')

@pytest.mark.version('>=4.0')
def test_1(act_1: Action, test_user: User, capsys):
    with act_1.db.connect(user=test_user.name, password=test_user.password) as con:
        c = con.cursor()
        c.execute('select rdb$time_zone_util.database_version() is not null as db_vers_defined from rdb$database')
        act_1.print_data_list(c)
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
