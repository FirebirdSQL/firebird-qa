#coding:utf-8

"""
ID:          issue-1716
ISSUE:       1716
TITLE:       Bad optimization of queries with DB_KEY
DESCRIPTION:
JIRA:        CORE-1295
FBTEST:      bugs.core_1295
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET PLANONLY;
select * from rdb$relations where rdb$db_key = ? and rdb$relation_id = 0;
select * from rdb$relations where rdb$db_key = ? and rdb$relation_name = 'RDB$RELATIONS';"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (RDB$RELATIONS INDEX ())
PLAN (RDB$RELATIONS INDEX ())
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

