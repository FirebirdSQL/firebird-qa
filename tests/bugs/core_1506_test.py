#coding:utf-8
#
# id:           bugs.core_1506
# title:        Server crash with isc_dsql_execute_immediate and zero length string
# decription:
#                   Confirmed on 2.1.0.17798, got:
#                       Error while executing SQL statement:
#
#               - SQLCODE: -902
#
#               - Unable to complete network request to host "localhost".
#
#               - Error reading data from the connection.
#                       -902, 335544721)
#                   firebird.log contains only this:
#                       CSPROG	Sat Mar 10 19:13:29 2018
#                       	INET/inet_error: read errno = 10054
#
#                   Checked on:
#                       2.5.9.27107: OK, 0.297s.
#                       3.0.4.32924: OK, 1.562s.
#                       4.0.0.918: OK, 1.735s.
#
#                   NB: FB 3.+ contain TWO messages with almost the same text about SQLSTATE = -104.
#                   Second line is filtered out - see 'substitutions' section.
#
# tracker_id:   CORE-1506
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DatabaseError

# version: 2.5
# resources: None

substitutions_1 = [('- SQL error code.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  try:
#      db_conn.execute_immediate('')
#  except Exception, e:
#      print( e[0] )
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Error while executing SQL statement:
    - SQLCODE: -104
    - Unexpected end of command
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    with act_1.db.connect() as con:
        with pytest.raises(DatabaseError, match='.*-Unexpected end of command.*'):
            con.execute_immediate('')


