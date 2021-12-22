#coding:utf-8
#
# id:           bugs.core_3973
# title:        Original table name and column name and owner missing from SQLDA for aliased column in grouped query
# decription:   
# tracker_id:   CORE-3973
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!name|table).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    set sqlda_display on;
    select rdb$relation_id as r_id, rdb$character_set_name
    from rdb$database
    group by rdb$relation_id, rdb$character_set_name; 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    :  name: RDB$RELATION_ID  alias: R_ID
    : table: RDB$DATABASE  owner: SYSDBA
    :  name: RDB$CHARACTER_SET_NAME  alias: RDB$CHARACTER_SET_NAME
    : table: RDB$DATABASE  owner: SYSDBA
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

