#coding:utf-8

"""
ID:          issue-6481
ISSUE:       6481
TITLE:       Performance problem when using SRP plugin
DESCRIPTION:
  :::::::::::::::::::: N O T A   B E N E  :::::::::::::::::
  It is crucial for this test that firebird.conf have following _SEQUENCE_ of auth-plugins:  Srp, ...,  Legacy_Auth
  -- i.e. Srp must be specified BEFORE Legacy.
  Slow time of attach establishing can NOT be seen otherwise; rather almost no difference will be in that case.
  :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

  Test creates two users: one usingLegacy plugin and second using Srp.
  Then we make ~20...30 pairs of attach/detach by each of these users and get total time difference for these actions.
  Ratio between these total differences must be limited with threshold. Its value was determined after dozen of runs
  and it seems to be reasonable assign to it value 1.25 (see MIN_RATIO_THRESHOLD in the code).

  Test output will contain ALERT if total time of <attaches_using_Srp> vs <attaches_using_Legacy>
  will be greater than MIN_RATIO_THRESHOLD.

  Reproduced on on several builds 4.x before 17.01.2020 (tested: 4.0.0.1712 CS, 4.0.0.1731 CS - got ratio = ~1.95).
  Reproduced also on 3.0.5.33221 Classic - got ratio ~1.50 ... 1.70; could NOT reproduce on 3.0.5 SuperClassic / SuperServer.
  JIRA:        CORE-6237
"""

import pytest
import datetime
from firebird.qa import *

db = db_factory()

leg_user = user_factory('db', name='tmp_c6237_leg', password='123', plugin='Legacy_UserManager')
srp_user = user_factory('db', name='tmp_c6237_srp', password='123', plugin='Srp')

act = python_act('db')

expected_stdout = """
    EXPECTED. Ratio of total elapsed time when use Srp vs Legacy is less then threshold.
"""

@pytest.mark.version('>=3.0.5')
def test_1(act: Action, leg_user: User, srp_user: User, capsys):
    N_ITER = 50
    MIN_RATIO_THRESHOLD = 1.41
    elapsed = {leg_user.name: 0, srp_user.name: 0}
    #
    for user in [leg_user, srp_user]:
        start = datetime.datetime.now()
        for i in range(N_ITER):
            with act.db.connect(user=user.name, password=user.password):
                pass
        stop = datetime.datetime.now()
        diff = stop - start
        elapsed[user.name] = int(diff.seconds) * 1000 + diff.microseconds / 1000
    #
    elapsed_time_ratio = 1.00 * elapsed[srp_user.name] / elapsed[leg_user.name]
    if  elapsed_time_ratio < MIN_RATIO_THRESHOLD:
        print('EXPECTED. Ratio of total elapsed time when use Srp vs Legacy is less then threshold.')
    else:
        print(f'Ratio Srp/Legacy: {elapsed_time_ratio} - is GREATER than threshold = {MIN_RATIO_THRESHOLD}. Total time spent for Srp: {elapsed[srp_user.name]} ms; for Legacy: {elapsed[leg_user.name]} ms.')
    #
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
