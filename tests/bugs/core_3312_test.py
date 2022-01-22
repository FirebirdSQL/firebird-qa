#coding:utf-8

"""
ID:          issue-3679
ISSUE:       3679
TITLE:       Sub-optimal join plan when the slave table depends on the master one via the OR predicate
DESCRIPTION:
JIRA:        CORE-3312
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET PLANONLY ON;
select *
from rdb$relations r
  join rdb$security_classes sc
    on (r.rdb$security_class = sc.rdb$security_class
      or r.rdb$default_class = sc.rdb$security_class);
select *
from rdb$relations r
  join rdb$security_classes sc
    on (r.rdb$security_class = sc.rdb$security_class and r.rdb$relation_id = 0)
      or (r.rdb$default_class = sc.rdb$security_class and r.rdb$relation_id = 1);
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN JOIN (R NATURAL, SC INDEX (RDB$INDEX_7, RDB$INDEX_7))
PLAN JOIN (R INDEX (RDB$INDEX_1, RDB$INDEX_1), SC INDEX (RDB$INDEX_7, RDB$INDEX_7))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

