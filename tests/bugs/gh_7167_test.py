#coding:utf-8

"""
ID:          issue-7167
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7167
TITLE:       Incorrect transliteration of field names in constraint violation errors
DESCRIPTION:
NOTES:
    [28.02.2023] pzotov
    Confirmed bug on 4.0.1.2692.
    Checked on 5.0.0.961, 4.0.3.2903 - all OK.
"""

import pytest
from firebird.qa import *

db = db_factory(charset = 'win1251')
act = python_act('db')

expected_stdout = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "уни" on table "абв"
    -Problematic key value is ("аб" = 'аб', "вг" = 'аб', "де" = 'аб')
"""
@pytest.mark.version('>=4.0.2')
def test_1(act: Action):
    test_sql = """
        create table "абв" (
            "аб" varchar(5) character set win1251,
            "вг" varchar(5) character set dos866,
            "де" varchar(5) character set utf8,
            constraint "уни" unique ("аб", "вг", "де")
        );
        insert into "абв" values ('аб','аб','аб');
        insert into "абв" values ('аб','аб','аб');
    """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], charset = 'win1251', input = test_sql, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
