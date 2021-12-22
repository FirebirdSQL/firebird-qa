#coding:utf-8
#
# id:           bugs.core_5028
# title:        Report the remote port number in MON$ATTACHMENTS
# decription:
#
# tracker_id:   CORE-5028
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  cur=db_conn.cursor()
#  sqlcmd='''
#  select iif(port > 0, 'OK', 'BAD') as port_value
#  from (
#      select cast(substring(mon$remote_address from 1 + position('/' in mon$remote_address)) as int) as port
#      from mon$attachments
#      where mon$attachment_id = current_connection
#  )
#  '''
#
#  # On previous FB versions <sqlcmd> will raise exception:
#  # Statement failed, SQLSTATE = 22018
#  # conversion error from string "192.168.43.154"
#
#  cur.execute(sqlcmd)
#  for r in cur:
#      print(r[0])
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    OK
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, capsys):
    with act_1.db.connect() as con:
        c = con.cursor()
        cmd = """
        select iif(port > 0, 'OK', 'BAD') as port_value
        from (
            select cast(substring(mon$remote_address from 1 + position('/' in mon$remote_address)) as int) as port
            from mon$attachments
            where mon$attachment_id = current_connection)
"""
        for row in c.execute(cmd):
            print(row[0])
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout


