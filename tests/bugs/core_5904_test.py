#coding:utf-8
#
# id:           bugs.core_5904
# title:        An attempt to create global mapping with long (greater than SQL identifier length) FROM field fails
# decription:   
#                   Confirmed bug on 3.0.4.33034.
#                   Checked on:
#                       3.0.4.33053: OK, 1.765s.
#                       4.0.0.1224: OK, 2.703s.
#                
# tracker_id:   CORE-5904
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set count on;
    set list on;
    set bail on;
    recreate view v_test as
    select 
        rdb$map_name, 
        rdb$map_using, 
        rdb$map_plugin, 
        rdb$map_db, 	
        rdb$map_from_type, 
        rdb$map_from, 
        rdb$map_to_type, 
        rdb$map_to 
    from rdb$auth_mapping;
    commit;    
    create or alter mapping krasnorutskayag using plugin win_sspi from user 'DOMN\\КрасноруцкаяАА' to user "DOMN\\Krasnorutskaya"; 
    create or alter global mapping krasnorutskayag using plugin win_sspi from user 'DOMN\\КрасноруцкаяАА' to user "DOMN\\Krasnorutskaya"; 
    commit;
    select * from v_test;
    drop mapping KrasnorutskayaG;
    drop global mapping KrasnorutskayaG;
    commit;  
    select * from v_test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$MAP_NAME                    KRASNORUTSKAYAG
    RDB$MAP_USING                   P
    RDB$MAP_PLUGIN                  WIN_SSPI
    RDB$MAP_DB                      <null>
    RDB$MAP_FROM_TYPE               USER
    RDB$MAP_FROM                    DOMN\\КрасноруцкаяАА
    RDB$MAP_TO_TYPE                 0
    RDB$MAP_TO                      DOMN\\Krasnorutskaya
    Records affected: 1
    Records affected: 0
"""

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

