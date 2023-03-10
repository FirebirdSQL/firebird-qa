#coding:utf-8

"""
ID:          issue-4038
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/4038
TITLE:       Wrong warning message for ambiguous query
DESCRIPTION: SQL dialect 1 allows such queries for backward compatibility reasons
JIRA:        CORE-3690
FBTEST:      bugs.core_3690
"""

import pytest
from firebird.qa import *

db_3 = db_factory(sql_dialect=3)

test_script = """
    set list on;
    select m.mon$sql_dialect from mon$database m;
    select 0*rdb$relation_id as id from rdb$database,rdb$database;
"""

act_3 = python_act('db_3')

expected_stdout_3 = """
    MON$SQL_DIALECT                 3

    Statement failed, SQLSTATE = 42702
    Dynamic SQL Error
    -SQL error code = -204
    -Ambiguous field name between table RDB$DATABASE and table RDB$DATABASE
    -RDB$RELATION_ID
"""

@pytest.mark.version('>=3')
def test_dialect_3(act_3: Action):
    act_3.expected_stdout = expected_stdout_3
    act_3.isql(switches=['-q', '-sql_dialect', '3'], input=test_script, combine_output=True)
    assert act_3.clean_stdout == act_3.clean_expected_stdout
