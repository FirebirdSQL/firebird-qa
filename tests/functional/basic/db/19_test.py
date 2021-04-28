#coding:utf-8
#
# id:           functional.basic.db.19
# title:        New DB - RDB$PROCEDURE_PARAMETERS
# decription:   
#                   Check for correct content of RDB$PROCEDURE_PARAMETERS in a new database.
#                   Checked on:
#                       2.5.9.27126: OK, 0.485s.
#                       3.0.5.33086: OK, 1.000s.
#                       4.0.0.1378: OK, 5.078s.
#                 
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_19

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
    from rdb$procedure_parameters
    order by rdb$procedure_name,rdb$parameter_name,rdb$parameter_number;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
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
    from rdb$procedure_parameters
    order by rdb$procedure_name,rdb$parameter_name,rdb$parameter_number;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """

    RDB$PARAMETER_NAME              RDB$DST_OFFSET                                                                                                                                                                                                                                              
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PARAMETER_NUMBER            3
    RDB$PARAMETER_TYPE              1
    RDB$FIELD_SOURCE                RDB$TIME_ZONE_OFFSET                                                                                                                                                                                                                                        
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$PARAMETER_MECHANISM         0
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          

    RDB$PARAMETER_NAME              RDB$EFFECTIVE_OFFSET                                                                                                                                                                                                                                        
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PARAMETER_NUMBER            4
    RDB$PARAMETER_TYPE              1
    RDB$FIELD_SOURCE                RDB$TIME_ZONE_OFFSET                                                                                                                                                                                                                                        
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$PARAMETER_MECHANISM         0
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          

    RDB$PARAMETER_NAME              RDB$END_TIMESTAMP                                                                                                                                                                                                                                           
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PARAMETER_NUMBER            1
    RDB$PARAMETER_TYPE              1
    RDB$FIELD_SOURCE                RDB$TIMESTAMP_TZ                                                                                                                                                                                                                                            
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$PARAMETER_MECHANISM         0
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          

    RDB$PARAMETER_NAME              RDB$FROM_TIMESTAMP                                                                                                                                                                                                                                          
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PARAMETER_NUMBER            1
    RDB$PARAMETER_TYPE              0
    RDB$FIELD_SOURCE                RDB$TIMESTAMP_TZ                                                                                                                                                                                                                                            
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$PARAMETER_MECHANISM         0
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          

    RDB$PARAMETER_NAME              RDB$START_TIMESTAMP                                                                                                                                                                                                                                         
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PARAMETER_NUMBER            0
    RDB$PARAMETER_TYPE              1
    RDB$FIELD_SOURCE                RDB$TIMESTAMP_TZ                                                                                                                                                                                                                                            
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$PARAMETER_MECHANISM         0
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          

    RDB$PARAMETER_NAME              RDB$TIME_ZONE_NAME                                                                                                                                                                                                                                          
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PARAMETER_NUMBER            0
    RDB$PARAMETER_TYPE              0
    RDB$FIELD_SOURCE                RDB$TIME_ZONE_NAME                                                                                                                                                                                                                                          
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$PARAMETER_MECHANISM         0
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          

    RDB$PARAMETER_NAME              RDB$TO_TIMESTAMP                                                                                                                                                                                                                                            
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PARAMETER_NUMBER            2
    RDB$PARAMETER_TYPE              0
    RDB$FIELD_SOURCE                RDB$TIMESTAMP_TZ                                                                                                                                                                                                                                            
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$PARAMETER_MECHANISM         0
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          

    RDB$PARAMETER_NAME              RDB$ZONE_OFFSET                                                                                                                                                                                                                                             
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PARAMETER_NUMBER            2
    RDB$PARAMETER_TYPE              1
    RDB$FIELD_SOURCE                RDB$TIME_ZONE_OFFSET                                                                                                                                                                                                                                        
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$DEFAULT_VALUE               <null>
    RDB$DEFAULT_SOURCE              <null>
    RDB$COLLATION_ID                <null>
    RDB$NULL_FLAG                   1
    RDB$PARAMETER_MECHANISM         0
    RDB$FIELD_NAME                  <null>
    RDB$RELATION_NAME               <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          

    Records affected: 8
  """

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

