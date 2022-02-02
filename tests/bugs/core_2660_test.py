#coding:utf-8

"""
ID:          issue-3066
ISSUE:       3066
TITLE:       COUNT(*) incorrectly returns 0 when a condition of an outer join doesn't match
DESCRIPTION:
JIRA:        CORE-2660
FBTEST:      bugs.core_2660
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

test_script = """select b.*
  from rdb$database a
  left join (
    select count(*) c
      from rdb$database
  ) b on 1 = 0;"""

act = isql_act('db', test_script)

expected_stdout = """
                    C
=====================
               <null>

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

