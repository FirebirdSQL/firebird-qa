#coding:utf-8

"""
ID:          session.alter-session-reset-raise-if-open-tx
ISSUE:       6093
TITLE:       ALTER SESSION RESET: throw error (isc_ses_reset_err) if any open transaction exist in current connection
DESCRIPTION:
  Test issue about ALTER SESSION RESET:
  "throw error (isc_ses_reset_err) if any open transaction exist in current connection except
  of current transaction..."

  We start three transactions within the same connection. First of them runs 'ALTER SESSION RESET'.
  It must fail with error with phrase about active transactions that prevent from doing this action.

  NOTE: this test does NOT check admissibility of session reset when prepared 2PC transactions exist.
  It checks only ERROR RAISING when there are several Tx opened within the same connection.
FBTEST:      functional.session.alter_session_reset_raise_if_open_tx
JIRA:        CORE-5832
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    Error while executing SQL statement:
    - SQLCODE: -901
    - Cannot reset user session
    - There are open transactions (3 active)
    -901
    335545206
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=4.0')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

# test_script_1
#---
#
#  tx1 = db_conn.trans()
#  tx2 = db_conn.trans()
#  tx3 = db_conn.trans()
#
#  tx1.begin()
#  tx2.begin()
#  tx3.begin()
#
#  cur1=tx1.cursor()
#  try:
#      cur1.execute('alter session reset')
#  except Exception,e:
#      for x in e:
#          print(x)
#  finally:
#      tx1.commit()
#      tx2.commit()
#      tx3.commit()
#
#  db_conn.close()
#
#---
