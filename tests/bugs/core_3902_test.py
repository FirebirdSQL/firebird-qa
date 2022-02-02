#coding:utf-8

"""
ID:          issue-4238
ISSUE:       4238
TITLE:       Derived fields may not be optimized via an index
DESCRIPTION:
JIRA:        CORE-3902
FBTEST:      bugs.core_3902
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET PLANONLY;
select rdb$database.rdb$relation_id from rdb$database
  left outer join
  ( select rdb$relations.rdb$relation_id as tempid
    from rdb$relations ) temp (tempid)
  on temp.tempid = rdb$database.rdb$relation_id;
select rdb$database.rdb$relation_id from rdb$database
  left outer join
  ( select rdb$relations.rdb$relation_id
    from rdb$relations ) temp
  on temp.rdb$relation_id = rdb$database.rdb$relation_id;

"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN JOIN (RDB$DATABASE NATURAL, TEMP RDB$RELATIONS INDEX (RDB$INDEX_1))
PLAN JOIN (RDB$DATABASE NATURAL, TEMP RDB$RELATIONS INDEX (RDB$INDEX_1))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

