#coding:utf-8

"""
ID:          issue-4038
ISSUE:       4038
TITLE:       Wrong warning message for ambiguous query
DESCRIPTION: SQL dialect 1 allows such queries for backward compatibility reasons
JIRA:        CORE-3690
FBTEST:      bugs.core_3690
"""

import pytest
from firebird.qa import *

db_1 = db_factory(sql_dialect=1)

test_script = """
    set list on;
    select m.mon$sql_dialect from mon$database m;
    select 0*rdb$relation_id as id from rdb$database,rdb$database;
"""

act_1 = python_act('db_1')

expected_stdout_1 = """
    MON$SQL_DIALECT                 1

    SQL warning code = 204
    -Ambiguous field name between table RDB$DATABASE and table RDB$DATABASE
    -RDB$RELATION_ID

    ID                              0
"""

@pytest.mark.version('>=3')
def test_dialect_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=['-q', '-sql_dialect', '1'], input=test_script, combine_output=True)
    assert act_1.clean_stdout == act_1.clean_expected_stdout
