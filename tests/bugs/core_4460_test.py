#coding:utf-8

"""
ID:          issue-4780
ISSUE:       4780
TITLE:       Expressions containing some built-in functions may be badly optimized
DESCRIPTION:
JIRA:        CORE-4460
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set planonly;
    select * from (
       select rdb$relation_name from rdb$relations
       union
       select rdb$field_name from rdb$fields
    ) as dt (name) where dt.name=''
    ;
    select * from (
      select rdb$relation_name from rdb$relations
      union
      select rdb$field_name from rdb$fields
    ) as dt (name) where dt.name = left('', 0)
    ;

    select * from (
      select rdb$relation_name from rdb$relations
      union
      select rdb$field_name from rdb$fields
    ) as dt (name) where dt.name = minvalue('', '')
    ;

    select * from (
      select rdb$relation_name from rdb$relations
      union
      select rdb$field_name from rdb$fields
    ) as dt (name) where dt.name = rpad('', 0, '')
    ;
"""

act = isql_act('db', test_script, substitutions=[('RDB\\$INDEX_[0-9]+', 'RDB\\$INDEX_')])

expected_stdout = """
    PLAN SORT (DT RDB$RELATIONS INDEX (RDB$INDEX_0), DT RDB$FIELDS INDEX (RDB$INDEX_2))
    PLAN SORT (DT RDB$RELATIONS INDEX (RDB$INDEX_0), DT RDB$FIELDS INDEX (RDB$INDEX_2))
    PLAN SORT (DT RDB$RELATIONS INDEX (RDB$INDEX_0), DT RDB$FIELDS INDEX (RDB$INDEX_2))
    PLAN SORT (DT RDB$RELATIONS INDEX (RDB$INDEX_0), DT RDB$FIELDS INDEX (RDB$INDEX_2))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

