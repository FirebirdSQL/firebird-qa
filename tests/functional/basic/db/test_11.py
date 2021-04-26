#coding:utf-8
#
# id:           functional.basic.db.db_11
# title:        New DB - RDB$FUNCTIONS
# decription:   
#                   Check for correct content of RDB$FUNCTIONS in a new database.
#                   Checked on:
#                       2.5.9.27126: OK, 1.734s.
#                       3.0.5.33086: OK, 1.250s.
#                       4.0.0.1378: OK, 5.422s.
#                
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_12

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select *
    from rdb$functions rf
    order by rdb$engine_name, rf.rdb$package_name, rf.rdb$function_name, rdb$module_name, rdb$entrypoint;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
 """

@pytest.mark.version('>=3.0,<4.0')
def test_db_11_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    set count on;
    select *
    from rdb$functions rf
    order by rdb$engine_name, rf.rdb$package_name, rf.rdb$function_name, rdb$module_name, rdb$entrypoint;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$FUNCTION_NAME               DATABASE_VERSION                                                                                                                                                                                                                                            
    RDB$FUNCTION_TYPE               <null>
    RDB$QUERY_NAME                  <null>
    RDB$DESCRIPTION                 <null>
    RDB$MODULE_NAME                 <null>
    RDB$ENTRYPOINT                  <null>
    RDB$RETURN_ARGUMENT             0
    RDB$SYSTEM_FLAG                 1
    RDB$ENGINE_NAME                 SYSTEM                                                                                                                                                                                                                                                      
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          
    RDB$PRIVATE_FLAG                0
    RDB$FUNCTION_SOURCE             <null>
    RDB$FUNCTION_ID                 1
    RDB$FUNCTION_BLR                <null>
    RDB$VALID_BLR                   1
    RDB$DEBUG_INFO                  <null>
    RDB$SECURITY_CLASS              <null>
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$LEGACY_FLAG                 <null>
    RDB$DETERMINISTIC_FLAG          <null>
    RDB$SQL_SECURITY                <null>

    Records affected: 1
 """

@pytest.mark.version('>=4.0')
def test_db_11_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

