#coding:utf-8
#
# id:           functional.basic.db.01
# title:        Empty DB - RDB$DATABASE content
# decription:   Check the correct content of RDB$DATABASE for freh, empty database.
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('RDB\\$SECURITY_CLASS[ ]+SQL\\$.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set blob all;
    select * from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$DESCRIPTION                 <null>
    RDB$RELATION_ID                 128
    RDB$SECURITY_CLASS              SQL$362
    RDB$CHARACTER_SET_NAME          NONE
    RDB$LINGER                      <null>
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = [('RDB\\$SECURITY_CLASS[ ]+SQL\\$.*', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    set blob all;
    select * from rdb$database;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$DESCRIPTION                 <null>
    RDB$RELATION_ID                 128
    RDB$SECURITY_CLASS              SQL$362
    RDB$CHARACTER_SET_NAME          NONE
    RDB$LINGER                      <null>
    RDB$SQL_SECURITY                <null>
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

