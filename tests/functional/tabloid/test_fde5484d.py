#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/fde5484d8f505d6d317f0e93860f3cc2765fe4e0
TITLE:       Increase isql max password length
DESCRIPTION:
    Test creates user with random password with length = maximal possible length minus 1 byte.
    Then we try to run isql and use such password as value for '-pass' command switch.
    Before fix, this failed with SQLSTATE = 28000 / Your user name and password are not defined.
NOTES:
    [04.02.2026] pzotov
    See letter from dimitr, 04.02.2026 10:57.
    It seems that there is a problem with password containing only one character: apostroph.
    To be investigated later.
    Checked on 6.0.0.1405-761a49d.
"""
import random
import string

import pytest
from firebird.qa import *

db = db_factory()

# see src/isql/isql.h:
# const int PASSWORD_LENGTH = ...
#
MAX_PASSWORD_LEN = 8191

# string.punctuation
# '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

tmp_user = user_factory('db', name = 'tmp$fde5484d', password = ''.join(random.choices('!"#$%&()*+,-./:;=?@[\\]^_`{|}~<>', k = MAX_PASSWORD_LEN)))
#tmp_user = user_factory('db', name = 'tmp$fde5484d', password = ''.join(random.choices("'", k = MAX_PASSWORD_LEN)))

substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_user: User, capsys):

    act.isql(switches = ['-q', '-user', tmp_user.name, '-pas', tmp_user.password.replace("'", "''"), act.db.dsn], input = 'set list on;select current_user as whoami from rdb$database;', connect_db = False, credentials = False, combine_output = True)

    expected_stdout = f"""
        WHOAMI {tmp_user.name.upper()}
    """
    act.expected_stdout = expected_stdout
    if act.clean_stdout == act.clean_expected_stdout:
        assert True
    else:
        print('Problem with transferring password detected.')
        print('ISQL output:\n\n' + act.clean_stdout)
        print('Password:\n' + tmp_user.password)
        assert capsys.readouterr().out == ''
