#coding:utf-8
#
# id:           functional.basic.db.11
# title:        New DB - RDB$FUNCTION_ARGUMENTS
# decription:   
#                   Check for correct content of RDB$FUNCTION_ARGUMENTS in a new database.
#                   Checked on:
#                       2.5.9.27126: OK, 0.656s.
#                       3.0.5.33086: OK, 1.156s.
#                       4.0.0.1378: OK, 5.344s.
#                
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_11

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
    from rdb$function_arguments fa
    order by fa.rdb$function_name, fa.rdb$argument_position;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    set count on;
    select *
    from rdb$function_arguments fa
    order by fa.rdb$function_name, fa.rdb$argument_position;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$FUNCTION_NAME               DATABASE_VERSION                                                                                                                                                                                                                                            
    RDB$ARGUMENT_POSITION           0
    RDB$MECHANISM                   <null>
    RDB$FIELD_TYPE                  <null>
    RDB$FIELD_SCALE                 <null>
    RDB$FIELD_LENGTH                <null>
    RDB$FIELD_SUB_TYPE              <null>
    RDB$CHARACTER_SET_ID            <null>
    RDB$FIELD_PRECISION             <null>
    RDB$CHARACTER_LENGTH            <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          
    RDB$ARGUMENT_NAME               <null>
    RDB$FIELD_SOURCE                RDB$DBTZ_VERSION                                                                                                                                                                                                                                            
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$ARGUMENT_MECHANISM          <null>
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DESCRIPTION                 <null>

    Records affected: 1
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

