#coding:utf-8

"""
ID:          issue-5406
ISSUE:       5406
TITLE:       Expression index may not be used by the optimizer if created and used in different connection charsets
DESCRIPTION:
JIRA:        CORE-5122
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    PLAN (TEST INDEX (TEST_CALC_S))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    with act.db.connect(charset='iso8859_1') as con1:
        cur1 = con1.cursor()
        cur1.execute("recreate table test(s varchar(10))")
        cur1.execute("create index test_calc_s on test computed by ('zxc' || s)")
        con1.commit()
    #
    act.expected_stdout = expected_stdout
    act.isql(switches=['-n'],
               input="set planonly; select * from test where 'zxc' || s starting with 'qwe';")
    assert act.clean_stdout == act.clean_expected_stdout
