#coding:utf-8

"""
ID:          issue-4306
ISSUE:       4306
TITLE:       Original table name and column name and owner missing from SQLDA for aliased column in grouped query
DESCRIPTION:
JIRA:        CORE-3973
FBTEST:      bugs.core_3973
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set planonly;
    set sqlda_display on;
    select rdb$relation_id as r_id, rdb$character_set_name
    from rdb$database
    group by rdb$relation_id, rdb$character_set_name;
"""

act = isql_act('db', test_script, substitutions=[('^((?!name|table).)*$', '')])

expected_stdout = """
    :  name: RDB$RELATION_ID  alias: R_ID
    : table: RDB$DATABASE  owner: SYSDBA
    :  name: RDB$CHARACTER_SET_NAME  alias: RDB$CHARACTER_SET_NAME
    : table: RDB$DATABASE  owner: SYSDBA
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

