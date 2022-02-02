#coding:utf-8

"""
ID:          issue-527
ISSUE:       527
TITLE:       Empty column names with aggregate funcs
DESCRIPTION:
JIRA:        CORE-200
FBTEST:      bugs.core_0200
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """select (select count(1) from rdb$database) from rdb$database ;
select (select avg(1) from rdb$database) from rdb$database ;
select (select sum(1) from rdb$database) from rdb$database ;
"""

act = isql_act('db', test_script)

expected_stdout = """                COUNT
=====================
                    1


                  AVG
=====================
                    1


                  SUM
=====================
                    1

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

