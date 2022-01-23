#coding:utf-8

"""
ID:          issue-4687
ISSUE:       4687
TITLE:       Equality predicate distribution does not work for some complex queries
DESCRIPTION:
JIRA:        CORE-4365
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set planonly;
    select *
    from (
      select r.rdb$relation_id as id
      from rdb$relations r
        join (
          select g1.rdb$generator_id as id from rdb$generators g1
          union all
          select g2.rdb$generator_id as id from rdb$generators g2
        ) rf on rf.id = r.rdb$relation_id
        left join rdb$procedures p on p.rdb$procedure_id = rf.id
    ) x
    where id = 1;
"""

act = isql_act('db', test_script, substitutions=[('RDB\\$INDEX_[0-9]+', 'RDB\\$INDEX')])

expected_stdout = """
    PLAN JOIN (JOIN (X RF G1 INDEX (RDB$INDEX_46), X RF G2 INDEX (RDB$INDEX_46), X R INDEX (RDB$INDEX_1)), X P INDEX (RDB$INDEX_22))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

