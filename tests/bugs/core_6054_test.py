#coding:utf-8

"""
ID:          issue-6304
ISSUE:       6304
TITLE:       Random crash 64bit fb_inet_server. Possible collation issue
DESCRIPTION:
JIRA:        CORE-6054
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table c (id int, f1 varchar(32) character set win1251 collate win1251);
    select * from c where f2 collate win1251_ua = 'x';
    set count on;
    select * from c where f1 = _utf8 'x';
"""

act = isql_act('db', test_script,
               substitutions=[('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+',
                               '-At line: column:')])

expected_stdout = """
    Records affected: 0
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -F2
    -At line: column:
"""

@pytest.mark.version('>=2.5.9')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
