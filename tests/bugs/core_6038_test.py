#coding:utf-8

"""
ID:          issue-6288
ISSUE:       6288
TITLE:       Srp user manager sporadically creates users which can not attach
  Explanation of bug nature was provided by Alex, see letter 05-jun-19 13:51.
  Some iteration failed with probability equal to occurence of 0 (zero) in the
  highest BYTE of some number. Byte is 8 bit ==> this probability is 1/256.
  Given 'N_LIMIT' is number of iterations, probability of success for ALL of
  them is 7.5%, and when N_LIMIT is 1000 then p = 0.004%.
  Because of time (speed) it was decided to run only 256 iterations. If bug
  will be 'raised' somewhere then this number is enough to catch it after 2-3
  times of test run.

  Reproduced on WI-V3.0.5.33118, date: 11-apr-19 (got fails not late than on 250th iteration).
  Works fine on WI-V3.0.5.33139, date: 04-apr-19.
NOTES:
  A new bug was found during this test implementation, affected 4.0 Classic only: CORE-6080.
DESCRIPTION:
JIRA:        CORE-6038
FBTEST:      bugs.core_6038
"""

import pytest
from firebird.qa import *

db_ = db_factory()

act = python_act('db_')

CHECK_USR = 'tmp$c6038_srp'
CHECK_PWD = 'QweRty#6038$='

@pytest.mark.version('>=3.0.5')
def test_1(act: Action):
    N_LIMIT = 256
    for i in range(N_LIMIT):
        with User(act.db, name=CHECK_USR, password=CHECK_PWD, plugin='Srp', charset='utf8'):
            with act.db.connect(user=CHECK_USR, password=CHECK_PWD):
                pass
    # Passed.

