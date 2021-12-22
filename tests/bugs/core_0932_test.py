#coding:utf-8
#
# id:           bugs.core_0932
# title:        Comment in create database
# decription:   Accept comment in Create database
# tracker_id:   CORE-932
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         bugs.core_932p

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    commit;
    create database /* foo */ '$(DATABASE_LOCATION)tmp_c0932_1.fdb';
    select iif( m.mon$database_name containing 'tmp_c0932_1', 'OK', 'FAIL' ) as result_1 from mon$database m;
    commit;
    drop database;
    create database /*/**//**/'$(DATABASE_LOCATION)tmp_c0932_2.fdb'/*/**//**//**//*/**/;
    select iif( m.mon$database_name containing 'tmp_c0932_2', 'OK', 'FAIL' ) as result_2 from mon$database m;
    commit;
    drop database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT_1                        OK
    RESULT_2                        OK
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

