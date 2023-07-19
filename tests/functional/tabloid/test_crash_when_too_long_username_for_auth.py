#coding:utf-8

"""
TITLE:       crash on assert or memory corruption when too long username is used for authentication
NOTES:
    [19.07.2023] pzotov
    Confirmed problem on 3.x only (3.0.11.33690).
    FB 4.0.3.2956 and 5.0.0.1093 (builds before 29-JUN-2023) issued "SQLSTATE = 28000 / Your user name and password..." but not crashed.
    After fix, all three FB issue "SQLSTATE = 08006 / Error occurred during login, please check server firebird.log for details"
    Checked on 3.0.11.33965 -- all OK.
"""
import locale
import re
from difflib import unified_diff

import pytest
from firebird.qa import *

db = db_factory() # charset = 'utf8', init = init_sql)

act = python_act( 'db', substitutions=[('[ \t]+',' ')] )

@pytest.mark.version('>=3.0.11')
def test_1(act: Action, capsys):

    MAX_NAME_LEN = 31 if act.is_version('<=3') else 63
    TOO_LONG_USR = 'u1111111111222222222233333333334444444444555555555566666666667777777777'
    test_sql = f"""
        connect '{act.db.dsn}' user '{TOO_LONG_USR}' password 'qqq';
        quit;
    """

    expected_stdout = """
        Statement failed, SQLSTATE = 08006
        Error occurred during login, please check server firebird.log for details
    """

    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], charset = 'win1251', credentials = False, connect_db = False, input = test_sql, combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
