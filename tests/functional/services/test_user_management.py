#coding:utf-8

"""
ID:          services.user-management
TITLE:       Check ability to make connect to FB services and add/drop user
DESCRIPTION:
  We check here:
  1) FB services features which add and remove user;
  2) Python firebird-driver functions (from class Server)

  NB.
  User with name 'tmp$test$user$' must NOT present in security_db.
  Correctness of adding user is verified by establishing TCP-based attachment to test DB using its login/password.

  See doc:
    https://firebird-driver.readthedocs.io/en/latest/usage-guide.html#user-maintenance
    https://firebird-driver.readthedocs.io/en/latest/ref-core.html#firebird.driver.core.Server.user
    https://firebird-driver.readthedocs.io/en/latest/ref-core.html#serveruserservices
FBTEST:      functional.services.user_management
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    Adding user.
    Done.
    Search in users list.
    Found user: TMP$TEST$USER$
    Trying to establish connection.
    TMP$TEST$USER$
    TCP
    Done.
    Removing user.
    Done.
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

# test_script_1
#---
#
#  import os
#  import subprocess
#  from fdb import services
#
#  TEST_USER_NAME='tmp$test$user$'.upper()
#  db_conn.close()
#
#  svc_con = services.connect( host='localhost', user = user_name, password = user_password )
#
#  u01 = services.User(TEST_USER_NAME)
#  u01.password = 'QweRty'
#  u01.first_name = 'Foo'
#  u01.last_name = 'Bar'
#
#
#  print('Adding user.')
#  svc_con.add_user(u01)
#  print('Done.')
#
#  usr_list = svc_con.get_users()
#  print('Search in users list.')
#  for u in usr_list:
#      if u.name == TEST_USER_NAME:
#          print('Found user:', u.name)
#
#  sql='''
#      select
#           mon$user as user_connected
#          ,iif( upper(mon$remote_protocol) starting with upper('TCP'), 'TCP', coalesce(mon$remote_protocol, '<NULL>') ) as protocol_info
#      from mon$attachments
#      where mon$attachment_id = current_connection
#  '''
#
#  try:
#      print('Trying to establish connection.')
#      usr_con = fdb.connect( dsn = dsn, user=TEST_USER_NAME, password='QweRty')
#      cur2 = usr_con.cursor()
#      cur2.execute( sql )
#      for r in cur2:
#          for i in range(0,len(r)):
#              print( ''.join( ( r[i] ) ) )
#      print('Done.')
#  finally:
#      usr_con.close()
#
#
#  print('Removing user.')
#  svc_con.remove_user(u01)
#  print('Done.')
#---
