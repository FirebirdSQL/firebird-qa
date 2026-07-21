#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9090
TITLE:       Firebird 6.0.0 inconsistencies re rdb$object_type 38 (SCHEMA)
DESCRIPTION:
NOTES:
    [20.07.2026] pzotov
    Confirmed issue on 6.0.0.2079-97c1429 (missed record in rdb$types).
    Checked on 6.0.0.2081-3217f44.
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

test_script = """
    set bail on;
    set list on;
    set count on;
    select t.* from rdb$types t
    where
        t.rdb$field_name = 'RDB$OBJECT_TYPE'
        and t.rdb$type_name = 'SCHEMA'
    order by rdb$field_name, rdb$type, rdb$type_name;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    RDB$FIELD_NAME  RDB$OBJECT_TYPE
    RDB$TYPE        38
    RDB$TYPE_NAME   SCHEMA
    RDB$DESCRIPTION <null>
    RDB$SYSTEM_FLAG 1
    Records affected: 1
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
