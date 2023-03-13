#coding:utf-8

"""
ID:          issue-4038-1
ISSUE:       4038
TITLE:       Wrong warning message for ambiguous query
DESCRIPTION: SQL dialect 1 allows such queries for backward compatibility reasons
JIRA:        CORE-3690
FBTEST:      bugs.core_3690_dialect_1
"""

import pytest
from firebird.qa import *

db = db_factory(sql_dialect=1)

test_script = """
    set list on;
    select m.mon$sql_dialect from mon$database m;
    select 0*rdb$relation_id as id from rdb$database,rdb$database;
"""

act = python_act('db')

expected_stdout = """
    MON$SQL_DIALECT                 1

    SQL warning code = 204
    -Ambiguous field name between table RDB$DATABASE and table RDB$DATABASE
    -RDB$RELATION_ID

    ID                              0
"""

@pytest.mark.version('>=3')
def test_dialect_1(act: Action):
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q', '-sql_dialect', '1'], input=test_script, combine_output=True)
    assert act.clean_stdout == act.clean_expected_stdout
