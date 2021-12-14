#coding:utf-8
#
# id:           bugs.core_6266
# title:        Deleting records from MON$ATTACHMENTS using ORDER BY clause doesn't close the corresponding attachments
# decription:
#                   Old title: Don't close attach while deleting record from MON$ATTACHMENTS using ORDER BY clause.
#                   Confirmed bug on 3.0.6.33271.
#                   Checked on 3.0.6.33272 (SS/CS) - works fine.
#                   22.04.2020. Checked separately on 4.0.0.1931 SS/CS: all OK. FB 4.0 can also be tested since this build.
#
# tracker_id:   CORE-6266
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
import time
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DatabaseError

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import time
#  import fdb
#
#  ATT_CNT=5
#  ATT_DELAY=1
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#  con_list={}
#  for i in range(0, ATT_CNT):
#      if i > 0:
#          time.sleep( ATT_DELAY )
#
#      c = fdb.connect(dsn = dsn)
#      a = c.attachment_id
#      con_list[ i ] = (a, c)
#      # print('created attachment ', (a,c) )
#
#  con_admin = con_list[0][1]
#
#  #print(con_admin.firebird_version)
#
#  # this removes ALL connections --> should NOT be used for reproducing ticket issue:
#  #con_admin.execute_immediate('delete from mon$attachments where mon$attachment_id != current_connection order by mon$timestamp')
#
#  # this removes ALL connections --> should NOT be used for reproducing ticket issue:
#  #con_admin.execute_immediate('delete from mon$attachments where mon$system_flag is distinct from 1 and mon$attachment_id != current_connection order by mon$timestamp')
#
#  # This DOES NOT remove all attachments (only 'last' in order of timestamp), but
#  # DELETE statement must NOT contain phrase 'mon$attachment_id != current_connection':
#  con_admin.execute_immediate('delete from mon$attachments where mon$system_flag is distinct from 1 order by mon$timestamp')
#
#  con_admin.commit()
#
#  cur_admin = con_admin.cursor()
#  cur_admin.execute('select mon$attachment_id,mon$user from mon$attachments where mon$system_flag is distinct from 1 and mon$attachment_id != current_connection' )
#  i=0
#  for r in cur_admin:
#      print( '### ACHTUNG ### STILL ALIVE ATTACHMENT DETECTED: ', r[0], r[1].strip(), '###' )
#      i += 1
#  print('Number of attachments that remains alive: ',i)
#
#  cur_admin.close()
#
#  #print('Final cleanup before quit from Python.')
#
#  for k,v in sorted(  con_list.items() ):
#      #print('attempt to close attachment ', v[0] )
#      try:
#          v[1].close()
#          #print('done.')
#      except Exception as e:
#          pass
#          #print('Got exception:', sys.exc_info()[0])
#          #print(e[0])
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Number of attachments that remains alive: 0
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, capsys):
    ATT_CNT = 5
    ATT_DELAY = 1
    #
    con_list = []
    for i in range(ATT_CNT):
        if i > 0:
            time.sleep(ATT_DELAY)
            con_list.append(act_1.db.connect())
    con_admin = con_list[0]
    # This DOES NOT remove all attachments (only 'last' in order of timestamp), but
    # DELETE statement must NOT contain phrase 'mon$attachment_id != current_connection':
    con_admin.execute_immediate('delete from mon$attachments where mon$system_flag is distinct from 1 order by mon$timestamp')
    con_admin.commit()
    #
    cur_admin = con_admin.cursor()
    cur_admin.execute('select mon$attachment_id,mon$user from mon$attachments where mon$system_flag is distinct from 1 and mon$attachment_id != current_connection')
    i = 0
    for r in cur_admin:
        print('STILL ALIVE ATTACHMENT DETECTED: ', r[0], r[1].strip())
        i += 1
    print(f'Number of attachments that remains alive: {i}')
    for con in con_list:
        try:
            con.close()
        except DatabaseError:
            pass
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
