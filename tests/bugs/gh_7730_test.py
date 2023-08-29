#coding:utf-8

"""
ID:          issue-7730
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7730
TITLE:       Server ignores the size of VARCHAR when performing SET BIND ... TO VARCHAR(N)
DESCRIPTION:
NOTES:
    [25.08.2023] pzotov
    Confirmed problem on 5.0.0.1169, 4.0.4.2982
    Checked on 5.0.0.1177, 4.0.4.2982 (intermediate snapshots).
"""

import locale
import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db', substitutions=[('^((?!sqltype:).)*$',''),('[ \t]+',' ')])

CHK_TIMESTAMP = '2023-08-29 01:02:03.0123 +03:00'
test_sql = f"""
    SET BIND OF TIMESTAMP WITH TIME ZONE TO varchar(128);
    set sqlda_display on;
    set planonly;
    select timestamp '{CHK_TIMESTAMP}' from rdb$database;
"""

expected_stdout = f"""
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 128 charset: 0 NONE
"""

@pytest.mark.version('>=4.0.4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input = test_sql, combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
