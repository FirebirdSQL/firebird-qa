#coding:utf-8
#
# id:           functional.basic.db.23
# title:        Empty DB - RDB$RELATIONS
# decription:   Check for correct content of RDB$RELATIONS in empty database.
# tracker_id:   
# min_versions: ['2.5.7']
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_23

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('VIEW_BLR_BLOB_ID.*', ''), ('VIEW_SRC_BLOB_ID.*', ''), ('DESCR_BLOB_ID.*', ''), ('RUNTIME_BLOB_ID.*', ''), ('EXT_DESCR_BLOB_ID.*', ''), ('RDB\\$TRIGGER_.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- 28.10.2015.
    -- 1. Removed from output BLOB IDs for fields rdb$security_class and rdb$default_class - they changes very often.
    -- 2. Added blocks to 'substitution' section to:
    -- 2.1  Suppress possible differences when check IDs of all BLOB fields.
    -- 2.2. Ignore values of IDs in lines like "trigger_name: RDB$TRIGGER_**".
    -- 3. Added query to select FIELDS list of table because main check does not use asterisk
    -- and we have to know if DDL of table will have any changes in future.

    set list on;
    set blob all;
    set count on;

    -- Query for check whether fields list of table was changed:
    select rf.rdb$field_name
    from rdb$relation_fields rf
    where rf.rdb$relation_name = upper('rdb$relations')
    order by rf.rdb$field_name;

    -- Main test query:
    select
        rdb$relation_id
        ,rdb$relation_name
        ,rdb$system_flag
        ,rdb$dbkey_length
        ,rdb$format
        ,rdb$field_id
        ,rdb$flags
        ,rdb$relation_type
        ,rdb$owner_name
        ,rdb$external_file
        ,rdb$view_blr             as view_blr_blob_id
        ,rdb$view_source          as view_src_blob_id
        ,rdb$description          as descr_blob_id
        ,rdb$runtime              as runtime_blob_id
        ,rdb$external_description as ext_descr_blob_id
        --,rdb$security_class
        --,rdb$default_class
    from rdb$relations
    order by rdb$relation_id;    
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """

    RDB$FIELD_NAME                  RDB$DBKEY_LENGTH                                                                             

    RDB$FIELD_NAME                  RDB$DEFAULT_CLASS                                                                            

    RDB$FIELD_NAME                  RDB$DESCRIPTION                                                                              

    RDB$FIELD_NAME                  RDB$EXTERNAL_DESCRIPTION                                                                     

    RDB$FIELD_NAME                  RDB$EXTERNAL_FILE                                                                            

    RDB$FIELD_NAME                  RDB$FIELD_ID                                                                                 

    RDB$FIELD_NAME                  RDB$FLAGS                                                                                    

    RDB$FIELD_NAME                  RDB$FORMAT                                                                                   

    RDB$FIELD_NAME                  RDB$OWNER_NAME                                                                               

    RDB$FIELD_NAME                  RDB$RELATION_ID                                                                              

    RDB$FIELD_NAME                  RDB$RELATION_NAME                                                                            

    RDB$FIELD_NAME                  RDB$RELATION_TYPE                                                                            

    RDB$FIELD_NAME                  RDB$RUNTIME                                                                                  

    RDB$FIELD_NAME                  RDB$SECURITY_CLASS                                                                           

    RDB$FIELD_NAME                  RDB$SYSTEM_FLAG                                                                              

    RDB$FIELD_NAME                  RDB$VIEW_BLR                                                                                 

    RDB$FIELD_NAME                  RDB$VIEW_SOURCE                                                                              


    Records affected: 17

    RDB$RELATION_ID                 0
    RDB$RELATION_NAME               RDB$PAGES                                                                                    
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 1
    RDB$RELATION_NAME               RDB$DATABASE                                                                                 
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    5
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 2
    RDB$RELATION_NAME               RDB$FIELDS                                                                                   
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    30
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e8
            	Field id: 0
            	    name: RDB$FIELD_NAME
            	Field id: 1
            	    name: RDB$QUERY_NAME
            	Field id: 2
            	    name: RDB$VALIDATION_BLR
            	Field id: 3
            	    name: RDB$VALIDATION_SOURCE
            	Field id: 4
            	    name: RDB$COMPUTED_BLR
            	Field id: 5
            	    name: RDB$COMPUTED_SOURCE
            	Field id: 6
            	    name: RDB$DEFAULT_VALUE
            	Field id: 7
            	    name: RDB$DEFAULT_SOURCE
            	Field id: 8
            	    name: RDB$FIELD_LENGTH
            	Field id: 9
            	    name: RDB$FIELD_SCALE
            	Field id: 10
            	    name: RDB$FIELD_TYPE
            	Field id: 11
            	    name: RDB$FIELD_SUB_TYPE
            	Field id: 12
            	    name: RDB$MISSING_VALUE
            	Field id: 13
            	    name: RDB$MISSING_SOURCE
            	Field id: 14
            	    name: RDB$DESCRIPTION
            	Field id: 15
            	    name: RDB$SYSTEM_FLAG
            	    field_not_null
            	Field id: 16
            	    name: RDB$QUERY_HEADER
            	Field id: 17
            	    name: RDB$SEGMENT_LENGTH
            	Field id: 18
            	    name: RDB$EDIT_STRING
            	Field id: 19
            	    name: RDB$EXTERNAL_LENGTH
            	Field id: 20
            	    name: RDB$EXTERNAL_SCALE
            	Field id: 21
            	    name: RDB$EXTERNAL_TYPE
            	Field id: 22
            	    name: RDB$DIMENSIONS
            	Field id: 23
            	    name: RDB$NULL_FLAG
            	Field id: 24
            	    name: RDB$CHARACTER_LENGTH
            	Field id: 25
            	    name: RDB$COLLATION_ID
            	Field id: 26
            	    name: RDB$CHARACTER_SET_ID
            	Field id: 27
            	    name: RDB$FIELD_PRECISION
            	Field id: 28
            	    name: RDB$SECURITY_CLASS
            	Field id: 29
            	    name: RDB$OWNER_NAME
            	    trigger_name: RDB$TRIGGER_36

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 3
    RDB$RELATION_NAME               RDB$INDEX_SEGMENTS                                                                           
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e5
            	Field id: 0
            	    name: RDB$INDEX_NAME
            	Field id: 1
            	    name: RDB$FIELD_NAME
            	Field id: 2
            	    name: RDB$FIELD_POSITION
            	Field id: 3
            	    name: RDB$STATISTICS
            	    trigger_name: RDB$TRIGGER_17
            	    trigger_name: RDB$TRIGGER_18

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 4
    RDB$RELATION_NAME               RDB$INDICES                                                                                  
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    13
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e6
            	Field id: 0
            	    name: RDB$INDEX_NAME
            	Field id: 1
            	    name: RDB$RELATION_NAME
            	Field id: 2
            	    name: RDB$INDEX_ID
            	Field id: 3
            	    name: RDB$UNIQUE_FLAG
            	Field id: 4
            	    name: RDB$DESCRIPTION
            	Field id: 5
            	    name: RDB$SEGMENT_COUNT
            	Field id: 6
            	    name: RDB$INDEX_INACTIVE
            	Field id: 7
            	    name: RDB$INDEX_TYPE
            	Field id: 8
            	    name: RDB$FOREIGN_KEY
            	Field id: 9
            	    name: RDB$SYSTEM_FLAG
            	    field_not_null
            	Field id: 10
            	    name: RDB$EXPRESSION_BLR
            	Field id: 11
            	    name: RDB$EXPRESSION_SOURCE
            	Field id: 12
            	    name: RDB$STATISTICS
            	    trigger_name: RDB$TRIGGER_19
            	    trigger_name: RDB$TRIGGER_20

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 5
    RDB$RELATION_NAME               RDB$RELATION_FIELDS                                                                          
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    21
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e7
            	Field id: 0
            	    name: RDB$FIELD_NAME
            	Field id: 1
            	    name: RDB$RELATION_NAME
            	Field id: 2
            	    name: RDB$FIELD_SOURCE
            	Field id: 3
            	    name: RDB$QUERY_NAME
            	Field id: 4
            	    name: RDB$BASE_FIELD
            	Field id: 5
            	    name: RDB$EDIT_STRING
            	Field id: 6
            	    name: RDB$FIELD_POSITION
            	Field id: 7
            	    name: RDB$QUERY_HEADER
            	Field id: 8
            	    name: RDB$UPDATE_FLAG
            	Field id: 9
            	    name: RDB$FIELD_ID
            	Field id: 10
            	    name: RDB$VIEW_CONTEXT
            	Field id: 11
            	    name: RDB$DESCRIPTION
            	Field id: 12
            	    name: RDB$DEFAULT_VALUE
            	Field id: 13
            	    name: RDB$SYSTEM_FLAG
            	    field_not_null
            	Field id: 14
            	    name: RDB$SECURITY_CLASS
            	Field id: 15
            	    name: RDB$COMPLEX_NAME
            	Field id: 16
            	    name: RDB$NULL_FLAG
            	Field id: 17
            	    name: RDB$DEFAULT_SOURCE
            	Field id: 18
            	    name: RDB$COLLATION_ID
            	Field id: 19
            	    name: RDB$GENERATOR_NAME
            	Field id: 20
            	    name: RDB$IDENTITY_TYPE
            	    trigger_name: RDB$TRIGGER_23
            	    trigger_name: RDB$TRIGGER_24
            	    trigger_name: RDB$TRIGGER_27

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 6
    RDB$RELATION_NAME               RDB$RELATIONS                                                                                
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    17
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 7
    RDB$RELATION_NAME               RDB$VIEW_RELATIONS                                                                           
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 8
    RDB$RELATION_NAME               RDB$FORMATS                                                                                  
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    3
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 9
    RDB$RELATION_NAME               RDB$SECURITY_CLASSES                                                                         
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    3
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 10
    RDB$RELATION_NAME               RDB$FILES                                                                                    
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 11
    RDB$RELATION_NAME               RDB$TYPES                                                                                    
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    5
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 12
    RDB$RELATION_NAME               RDB$TRIGGERS                                                                                 
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    14
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e1
            	Field id: 0
            	    name: RDB$TRIGGER_NAME
            	Field id: 1
            	    name: RDB$RELATION_NAME
            	Field id: 2
            	    name: RDB$TRIGGER_SEQUENCE
            	Field id: 3
            	    name: RDB$TRIGGER_TYPE
            	Field id: 4
            	    name: RDB$TRIGGER_SOURCE
            	Field id: 5
            	    name: RDB$TRIGGER_BLR
            	Field id: 6
            	    name: RDB$DESCRIPTION
            	Field id: 7
            	    name: RDB$TRIGGER_INACTIVE
            	Field id: 8
            	    name: RDB$SYSTEM_FLAG
            	    field_not_null
            	Field id: 9
            	    name: RDB$FLAGS
            	Field id: 10
            	    name: RDB$VALID_BLR
            	Field id: 11
            	    name: RDB$DEBUG_INFO
            	Field id: 12
            	    name: RDB$ENGINE_NAME
            	Field id: 13
            	    name: RDB$ENTRYPOINT
            	    trigger_name: RDB$TRIGGER_2
            	    trigger_name: RDB$TRIGGER_21
            	    trigger_name: RDB$TRIGGER_22
            	    trigger_name: RDB$TRIGGER_3

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 13
    RDB$RELATION_NAME               RDB$DEPENDENCIES                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 14
    RDB$RELATION_NAME               RDB$FUNCTIONS                                                                                
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    20
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 15
    RDB$RELATION_NAME               RDB$FUNCTION_ARGUMENTS                                                                       
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    22
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 16
    RDB$RELATION_NAME               RDB$FILTERS                                                                                  
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    9
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 17
    RDB$RELATION_NAME               RDB$TRIGGER_MESSAGES                                                                         
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    3
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 18
    RDB$RELATION_NAME               RDB$USER_PRIVILEGES                                                                          
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e0
            	Field id: 0
            	    name: RDB$USER
            	Field id: 1
            	    name: RDB$GRANTOR
            	Field id: 2
            	    name: RDB$PRIVILEGE
            	Field id: 3
            	    name: RDB$GRANT_OPTION
            	Field id: 4
            	    name: RDB$RELATION_NAME
            	Field id: 5
            	    name: RDB$FIELD_NAME
            	Field id: 6
            	    name: RDB$USER_TYPE
            	Field id: 7
            	    name: RDB$OBJECT_TYPE
            	    trigger_name: RDB$TRIGGER_1
            	    trigger_name: RDB$TRIGGER_31
            	    trigger_name: RDB$TRIGGER_32
            	    trigger_name: RDB$TRIGGER_33
            	    trigger_name: RDB$TRIGGER_8
            	    trigger_name: RDB$TRIGGER_9

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 19
    RDB$RELATION_NAME               RDB$TRANSACTIONS                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 20
    RDB$RELATION_NAME               RDB$GENERATORS                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 21
    RDB$RELATION_NAME               RDB$FIELD_DIMENSIONS                                                                         
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 22
    RDB$RELATION_NAME               RDB$RELATION_CONSTRAINTS                                                                     
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e2
            	Field id: 0
            	    name: RDB$CONSTRAINT_NAME
            	Field id: 1
            	    name: RDB$CONSTRAINT_TYPE
            	Field id: 2
            	    name: RDB$RELATION_NAME
            	Field id: 3
            	    name: RDB$DEFERRABLE
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 2,0, 'N','O',
            	        blr_eoc
            	Field id: 4
            	    name: RDB$INITIALLY_DEFERRED
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 2,0, 'N','O',
            	        blr_eoc
            	Field id: 5
            	    name: RDB$INDEX_NAME
            	    trigger_name: RDB$TRIGGER_10
            	    trigger_name: RDB$TRIGGER_11
            	    trigger_name: RDB$TRIGGER_25
            	    trigger_name: RDB$TRIGGER_26
            	    trigger_name: RDB$TRIGGER_34

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 23
    RDB$RELATION_NAME               RDB$REF_CONSTRAINTS                                                                          
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    5
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e3
            	Field id: 0
            	    name: RDB$CONSTRAINT_NAME
            	Field id: 1
            	    name: RDB$CONST_NAME_UQ
            	Field id: 2
            	    name: RDB$MATCH_OPTION
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 4,0, 'F','U','L','L',
            	        blr_eoc
            	Field id: 3
            	    name: RDB$UPDATE_RULE
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 8,0, 'R','E','S','T','R','I','C','T',
            	        blr_eoc
            	Field id: 4
            	    name: RDB$DELETE_RULE
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 8,0, 'R','E','S','T','R','I','C','T',
            	        blr_eoc
            	    trigger_name: RDB$TRIGGER_12
            	    trigger_name: RDB$TRIGGER_13

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 24
    RDB$RELATION_NAME               RDB$CHECK_CONSTRAINTS                                                                        
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    2
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e4
            	Field id: 0
            	    name: RDB$CONSTRAINT_NAME
            	Field id: 1
            	    name: RDB$TRIGGER_NAME
            	    trigger_name: RDB$TRIGGER_14
            	    trigger_name: RDB$TRIGGER_15
            	    trigger_name: RDB$TRIGGER_16
            	    trigger_name: RDB$TRIGGER_35

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 25
    RDB$RELATION_NAME               RDB$LOG_FILES                                                                                
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 26
    RDB$RELATION_NAME               RDB$PROCEDURES                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    18
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 27
    RDB$RELATION_NAME               RDB$PROCEDURE_PARAMETERS                                                                     
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    15
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 28
    RDB$RELATION_NAME               RDB$CHARACTER_SETS                                                                           
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    11
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 29
    RDB$RELATION_NAME               RDB$COLLATIONS                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    11
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 30
    RDB$RELATION_NAME               RDB$EXCEPTIONS                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    7
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 31
    RDB$RELATION_NAME               RDB$ROLES                                                                                    
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    5
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 32
    RDB$RELATION_NAME               RDB$BACKUP_HISTORY                                                                           
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 33
    RDB$RELATION_NAME               MON$DATABASE                                                                                 
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    22
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 34
    RDB$RELATION_NAME               MON$ATTACHMENTS                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    20
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 35
    RDB$RELATION_NAME               MON$TRANSACTIONS                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    13
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 36
    RDB$RELATION_NAME               MON$STATEMENTS                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 37
    RDB$RELATION_NAME               MON$CALL_STACK                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    10
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 38
    RDB$RELATION_NAME               MON$IO_STATS                                                                                 
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 39
    RDB$RELATION_NAME               MON$RECORD_STATS                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    16
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 40
    RDB$RELATION_NAME               MON$CONTEXT_VARIABLES                                                                        
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 41
    RDB$RELATION_NAME               MON$MEMORY_USAGE                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 42
    RDB$RELATION_NAME               RDB$PACKAGES                                                                                 
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 43
    RDB$RELATION_NAME               SEC$USERS                                                                                    
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 44
    RDB$RELATION_NAME               SEC$USER_ATTRIBUTES                                                                          
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 45
    RDB$RELATION_NAME               RDB$AUTH_MAPPING                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    10
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 46
    RDB$RELATION_NAME               SEC$GLOBAL_AUTH_MAPPING                                                                      
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 47
    RDB$RELATION_NAME               RDB$DB_CREATORS                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    2
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 48
    RDB$RELATION_NAME               SEC$DB_CREATORS                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    2
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 49
    RDB$RELATION_NAME               MON$TABLE_STATS                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                       
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>


    Records affected: 50
  """

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('VIEW_BLR_BLOB_ID.*', ''), ('VIEW_SRC_BLOB_ID.*', ''), ('DESCR_BLOB_ID.*', ''), ('RUNTIME_BLOB_ID.*', ''), ('EXT_DESCR_BLOB_ID.*', ''), ('RDB\\$TRIGGER_.*', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    -- 28.10.2015.
    -- 1. Removed from output BLOB IDs for fields rdb$security_class and rdb$default_class - they changes very often.
    -- 2. Added blocks to 'substitution' section to:
    -- 2.1  Suppress possible differences when check IDs of all BLOB fields.
    -- 2.2. Ignore values of IDs in lines like "trigger_name: RDB$TRIGGER_**".
    -- 3. Added query to select FIELDS list of table because main check does not use asterisk
    -- and we have to know if DDL of table will have any changes in future.

    set list on;
    set blob all;
    set count on;

    -- Query for check whether fields list of table was changed:
    select rf.rdb$field_name
    from rdb$relation_fields rf
    where rf.rdb$relation_name = upper('rdb$relations')
    order by rf.rdb$field_name;

    -- Main test query.
    -- NB: rdb$relation_name is unique column, see DDL:
    -- ALTER TABLE RDB$RELATIONS ADD CONSTRAINT RDB$INDEX_0 UNIQUE (RDB$RELATION_NAME);
    select
        rdb$relation_id
        ,rdb$relation_name
        ,rdb$system_flag
        ,rdb$dbkey_length
        ,rdb$format
        ,rdb$field_id
        ,rdb$flags
        ,rdb$relation_type
        ,rdb$owner_name
        ,rdb$external_file
        ,rdb$view_blr             as view_blr_blob_id
        ,rdb$view_source          as view_src_blob_id
        ,rdb$description          as descr_blob_id
        ,rdb$runtime              as runtime_blob_id
        ,rdb$external_description as ext_descr_blob_id
        --,rdb$security_class
        --,rdb$default_class
    from rdb$relations
    order by RDB$RELATION_NAME;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """

    RDB$FIELD_NAME                  RDB$DBKEY_LENGTH                                                                                                                                                                                                                                            

    RDB$FIELD_NAME                  RDB$DEFAULT_CLASS                                                                                                                                                                                                                                           

    RDB$FIELD_NAME                  RDB$DESCRIPTION                                                                                                                                                                                                                                             

    RDB$FIELD_NAME                  RDB$EXTERNAL_DESCRIPTION                                                                                                                                                                                                                                    

    RDB$FIELD_NAME                  RDB$EXTERNAL_FILE                                                                                                                                                                                                                                           

    RDB$FIELD_NAME                  RDB$FIELD_ID                                                                                                                                                                                                                                                

    RDB$FIELD_NAME                  RDB$FLAGS                                                                                                                                                                                                                                                   

    RDB$FIELD_NAME                  RDB$FORMAT                                                                                                                                                                                                                                                  

    RDB$FIELD_NAME                  RDB$OWNER_NAME                                                                                                                                                                                                                                              

    RDB$FIELD_NAME                  RDB$RELATION_ID                                                                                                                                                                                                                                             

    RDB$FIELD_NAME                  RDB$RELATION_NAME                                                                                                                                                                                                                                           

    RDB$FIELD_NAME                  RDB$RELATION_TYPE                                                                                                                                                                                                                                           

    RDB$FIELD_NAME                  RDB$RUNTIME                                                                                                                                                                                                                                                 

    RDB$FIELD_NAME                  RDB$SECURITY_CLASS                                                                                                                                                                                                                                          

    RDB$FIELD_NAME                  RDB$SQL_SECURITY                                                                                                                                                                                                                                            

    RDB$FIELD_NAME                  RDB$SYSTEM_FLAG                                                                                                                                                                                                                                             

    RDB$FIELD_NAME                  RDB$VIEW_BLR                                                                                                                                                                                                                                                

    RDB$FIELD_NAME                  RDB$VIEW_SOURCE                                                                                                                                                                                                                                             


    Records affected: 18

    RDB$RELATION_ID                 34
    RDB$RELATION_NAME               MON$ATTACHMENTS                                                                                                                                                                                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    26
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 37
    RDB$RELATION_NAME               MON$CALL_STACK                                                                                                                                                                                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    10
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 40
    RDB$RELATION_NAME               MON$CONTEXT_VARIABLES                                                                                                                                                                                                                                       
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 33
    RDB$RELATION_NAME               MON$DATABASE                                                                                                                                                                                                                                                
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    28
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 38
    RDB$RELATION_NAME               MON$IO_STATS                                                                                                                                                                                                                                                
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 41
    RDB$RELATION_NAME               MON$MEMORY_USAGE                                                                                                                                                                                                                                            
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 39
    RDB$RELATION_NAME               MON$RECORD_STATS                                                                                                                                                                                                                                            
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    17
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 36
    RDB$RELATION_NAME               MON$STATEMENTS                                                                                                                                                                                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    10
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 49
    RDB$RELATION_NAME               MON$TABLE_STATS                                                                                                                                                                                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 35
    RDB$RELATION_NAME               MON$TRANSACTIONS                                                                                                                                                                                                                                            
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    13
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 45
    RDB$RELATION_NAME               RDB$AUTH_MAPPING                                                                                                                                                                                                                                            
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    10
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 32
    RDB$RELATION_NAME               RDB$BACKUP_HISTORY                                                                                                                                                                                                                                          
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 28
    RDB$RELATION_NAME               RDB$CHARACTER_SETS                                                                                                                                                                                                                                          
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    11
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 24
    RDB$RELATION_NAME               RDB$CHECK_CONSTRAINTS                                                                                                                                                                                                                                       
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    2
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e4
            	Field id: 0
            	    name: RDB$CONSTRAINT_NAME
            	Field id: 1
            	    name: RDB$TRIGGER_NAME
            	    trigger_name: RDB$TRIGGER_14
            	    trigger_name: RDB$TRIGGER_15
            	    trigger_name: RDB$TRIGGER_35
            	    trigger_name: RDB$TRIGGER_16

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 29
    RDB$RELATION_NAME               RDB$COLLATIONS                                                                                                                                                                                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    11
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 53
    RDB$RELATION_NAME               RDB$CONFIG                                                                                                                                                                                                                                                  
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 1
    RDB$RELATION_NAME               RDB$DATABASE                                                                                                                                                                                                                                                
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 47
    RDB$RELATION_NAME               RDB$DB_CREATORS                                                                                                                                                                                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    2
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 13
    RDB$RELATION_NAME               RDB$DEPENDENCIES                                                                                                                                                                                                                                            
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 30
    RDB$RELATION_NAME               RDB$EXCEPTIONS                                                                                                                                                                                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    7
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 2
    RDB$RELATION_NAME               RDB$FIELDS                                                                                                                                                                                                                                                  
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    30
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e8
            	Field id: 0
            	    name: RDB$FIELD_NAME
            	Field id: 1
            	    name: RDB$QUERY_NAME
            	Field id: 2
            	    name: RDB$VALIDATION_BLR
            	Field id: 3
            	    name: RDB$VALIDATION_SOURCE
            	Field id: 4
            	    name: RDB$COMPUTED_BLR
            	Field id: 5
            	    name: RDB$COMPUTED_SOURCE
            	Field id: 6
            	    name: RDB$DEFAULT_VALUE
            	Field id: 7
            	    name: RDB$DEFAULT_SOURCE
            	Field id: 8
            	    name: RDB$FIELD_LENGTH
            	Field id: 9
            	    name: RDB$FIELD_SCALE
            	Field id: 10
            	    name: RDB$FIELD_TYPE
            	Field id: 11
            	    name: RDB$FIELD_SUB_TYPE
            	Field id: 12
            	    name: RDB$MISSING_VALUE
            	Field id: 13
            	    name: RDB$MISSING_SOURCE
            	Field id: 14
            	    name: RDB$DESCRIPTION
            	Field id: 15
            	    name: RDB$SYSTEM_FLAG
            	    field_not_null
            	Field id: 16
            	    name: RDB$QUERY_HEADER
            	Field id: 17
            	    name: RDB$SEGMENT_LENGTH
            	Field id: 18
            	    name: RDB$EDIT_STRING
            	Field id: 19
            	    name: RDB$EXTERNAL_LENGTH
            	Field id: 20
            	    name: RDB$EXTERNAL_SCALE
            	Field id: 21
            	    name: RDB$EXTERNAL_TYPE
            	Field id: 22
            	    name: RDB$DIMENSIONS
            	Field id: 23
            	    name: RDB$NULL_FLAG
            	Field id: 24
            	    name: RDB$CHARACTER_LENGTH
            	Field id: 25
            	    name: RDB$COLLATION_ID
            	Field id: 26
            	    name: RDB$CHARACTER_SET_ID
            	Field id: 27
            	    name: RDB$FIELD_PRECISION
            	Field id: 28
            	    name: RDB$SECURITY_CLASS
            	Field id: 29
            	    name: RDB$OWNER_NAME
            	    trigger_name: RDB$TRIGGER_36

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 21
    RDB$RELATION_NAME               RDB$FIELD_DIMENSIONS                                                                                                                                                                                                                                        
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 10
    RDB$RELATION_NAME               RDB$FILES                                                                                                                                                                                                                                                   
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 16
    RDB$RELATION_NAME               RDB$FILTERS                                                                                                                                                                                                                                                 
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    9
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 8
    RDB$RELATION_NAME               RDB$FORMATS                                                                                                                                                                                                                                                 
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    3
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 14
    RDB$RELATION_NAME               RDB$FUNCTIONS                                                                                                                                                                                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    21
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 15
    RDB$RELATION_NAME               RDB$FUNCTION_ARGUMENTS                                                                                                                                                                                                                                      
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    22
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 20
    RDB$RELATION_NAME               RDB$GENERATORS                                                                                                                                                                                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 3
    RDB$RELATION_NAME               RDB$INDEX_SEGMENTS                                                                                                                                                                                                                                          
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e5
            	Field id: 0
            	    name: RDB$INDEX_NAME
            	Field id: 1
            	    name: RDB$FIELD_NAME
            	Field id: 2
            	    name: RDB$FIELD_POSITION
            	Field id: 3
            	    name: RDB$STATISTICS
            	    trigger_name: RDB$TRIGGER_17
            	    trigger_name: RDB$TRIGGER_18

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 4
    RDB$RELATION_NAME               RDB$INDICES                                                                                                                                                                                                                                                 
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    13
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e6
            	Field id: 0
            	    name: RDB$INDEX_NAME
            	Field id: 1
            	    name: RDB$RELATION_NAME
            	Field id: 2
            	    name: RDB$INDEX_ID
            	Field id: 3
            	    name: RDB$UNIQUE_FLAG
            	Field id: 4
            	    name: RDB$DESCRIPTION
            	Field id: 5
            	    name: RDB$SEGMENT_COUNT
            	Field id: 6
            	    name: RDB$INDEX_INACTIVE
            	Field id: 7
            	    name: RDB$INDEX_TYPE
            	Field id: 8
            	    name: RDB$FOREIGN_KEY
            	Field id: 9
            	    name: RDB$SYSTEM_FLAG
            	    field_not_null
            	Field id: 10
            	    name: RDB$EXPRESSION_BLR
            	Field id: 11
            	    name: RDB$EXPRESSION_SOURCE
            	Field id: 12
            	    name: RDB$STATISTICS
            	    trigger_name: RDB$TRIGGER_20
            	    trigger_name: RDB$TRIGGER_19

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 25
    RDB$RELATION_NAME               RDB$LOG_FILES                                                                                                                                                                                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 42
    RDB$RELATION_NAME               RDB$PACKAGES                                                                                                                                                                                                                                                
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    9
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 0
    RDB$RELATION_NAME               RDB$PAGES                                                                                                                                                                                                                                                   
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 26
    RDB$RELATION_NAME               RDB$PROCEDURES                                                                                                                                                                                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    19
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 27
    RDB$RELATION_NAME               RDB$PROCEDURE_PARAMETERS                                                                                                                                                                                                                                    
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    15
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 51
    RDB$RELATION_NAME               RDB$PUBLICATIONS                                                                                                                                                                                                                                            
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    5
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 52
    RDB$RELATION_NAME               RDB$PUBLICATION_TABLES                                                                                                                                                                                                                                      
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    2
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 23
    RDB$RELATION_NAME               RDB$REF_CONSTRAINTS                                                                                                                                                                                                                                         
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    5
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e3
            	Field id: 0
            	    name: RDB$CONSTRAINT_NAME
            	Field id: 1
            	    name: RDB$CONST_NAME_UQ
            	Field id: 2
            	    name: RDB$MATCH_OPTION
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 4,0, 'F','U','L','L',
            	        blr_eoc
            	Field id: 3
            	    name: RDB$UPDATE_RULE
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 8,0, 'R','E','S','T','R','I','C','T',
            	        blr_eoc
            	Field id: 4
            	    name: RDB$DELETE_RULE
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 8,0, 'R','E','S','T','R','I','C','T',
            	        blr_eoc
            	    trigger_name: RDB$TRIGGER_12
            	    trigger_name: RDB$TRIGGER_13

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 6
    RDB$RELATION_NAME               RDB$RELATIONS                                                                                                                                                                                                                                               
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    18
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 22
    RDB$RELATION_NAME               RDB$RELATION_CONSTRAINTS                                                                                                                                                                                                                                    
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e2
            	Field id: 0
            	    name: RDB$CONSTRAINT_NAME
            	Field id: 1
            	    name: RDB$CONSTRAINT_TYPE
            	Field id: 2
            	    name: RDB$RELATION_NAME
            	Field id: 3
            	    name: RDB$DEFERRABLE
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 2,0, 'N','O',
            	        blr_eoc
            	Field id: 4
            	    name: RDB$INITIALLY_DEFERRED
            	    default_value:
            	        blr_version5,
            	        blr_literal, blr_text2, 2,0, 2,0, 'N','O',
            	        blr_eoc
            	Field id: 5
            	    name: RDB$INDEX_NAME
            	    trigger_name: RDB$TRIGGER_10
            	    trigger_name: RDB$TRIGGER_11
            	    trigger_name: RDB$TRIGGER_34
            	    trigger_name: RDB$TRIGGER_25
            	    trigger_name: RDB$TRIGGER_26

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 5
    RDB$RELATION_NAME               RDB$RELATION_FIELDS                                                                                                                                                                                                                                         
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    21
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e7
            	Field id: 0
            	    name: RDB$FIELD_NAME
            	Field id: 1
            	    name: RDB$RELATION_NAME
            	Field id: 2
            	    name: RDB$FIELD_SOURCE
            	Field id: 3
            	    name: RDB$QUERY_NAME
            	Field id: 4
            	    name: RDB$BASE_FIELD
            	Field id: 5
            	    name: RDB$EDIT_STRING
            	Field id: 6
            	    name: RDB$FIELD_POSITION
            	Field id: 7
            	    name: RDB$QUERY_HEADER
            	Field id: 8
            	    name: RDB$UPDATE_FLAG
            	Field id: 9
            	    name: RDB$FIELD_ID
            	Field id: 10
            	    name: RDB$VIEW_CONTEXT
            	Field id: 11
            	    name: RDB$DESCRIPTION
            	Field id: 12
            	    name: RDB$DEFAULT_VALUE
            	Field id: 13
            	    name: RDB$SYSTEM_FLAG
            	    field_not_null
            	Field id: 14
            	    name: RDB$SECURITY_CLASS
            	Field id: 15
            	    name: RDB$COMPLEX_NAME
            	Field id: 16
            	    name: RDB$NULL_FLAG
            	Field id: 17
            	    name: RDB$DEFAULT_SOURCE
            	Field id: 18
            	    name: RDB$COLLATION_ID
            	Field id: 19
            	    name: RDB$GENERATOR_NAME
            	Field id: 20
            	    name: RDB$IDENTITY_TYPE
            	    trigger_name: RDB$TRIGGER_23
            	    trigger_name: RDB$TRIGGER_24
            	    trigger_name: RDB$TRIGGER_27

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 31
    RDB$RELATION_NAME               RDB$ROLES                                                                                                                                                                                                                                                   
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 9
    RDB$RELATION_NAME               RDB$SECURITY_CLASSES                                                                                                                                                                                                                                        
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    3
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 50
    RDB$RELATION_NAME               RDB$TIME_ZONES                                                                                                                                                                                                                                              
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    2
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 19
    RDB$RELATION_NAME               RDB$TRANSACTIONS                                                                                                                                                                                                                                            
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 12
    RDB$RELATION_NAME               RDB$TRIGGERS                                                                                                                                                                                                                                                
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    15
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e1
            	Field id: 0
            	    name: RDB$TRIGGER_NAME
            	Field id: 1
            	    name: RDB$RELATION_NAME
            	Field id: 2
            	    name: RDB$TRIGGER_SEQUENCE
            	Field id: 3
            	    name: RDB$TRIGGER_TYPE
            	Field id: 4
            	    name: RDB$TRIGGER_SOURCE
            	Field id: 5
            	    name: RDB$TRIGGER_BLR
            	Field id: 6
            	    name: RDB$DESCRIPTION
            	Field id: 7
            	    name: RDB$TRIGGER_INACTIVE
            	Field id: 8
            	    name: RDB$SYSTEM_FLAG
            	    field_not_null
            	Field id: 9
            	    name: RDB$FLAGS
            	Field id: 10
            	    name: RDB$VALID_BLR
            	Field id: 11
            	    name: RDB$DEBUG_INFO
            	Field id: 12
            	    name: RDB$ENGINE_NAME
            	Field id: 13
            	    name: RDB$ENTRYPOINT
            	Field id: 14
            	    name: RDB$SQL_SECURITY
            	    trigger_name: RDB$TRIGGER_2
            	    trigger_name: RDB$TRIGGER_3
            	    trigger_name: RDB$TRIGGER_21
            	    trigger_name: RDB$TRIGGER_22

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 17
    RDB$RELATION_NAME               RDB$TRIGGER_MESSAGES                                                                                                                                                                                                                                        
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    3
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 11
    RDB$RELATION_NAME               RDB$TYPES                                                                                                                                                                                                                                                   
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    5
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 18
    RDB$RELATION_NAME               RDB$USER_PRIVILEGES                                                                                                                                                                                                                                         
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 6:1e0
            	Field id: 0
            	    name: RDB$USER
            	Field id: 1
            	    name: RDB$GRANTOR
            	Field id: 2
            	    name: RDB$PRIVILEGE
            	Field id: 3
            	    name: RDB$GRANT_OPTION
            	Field id: 4
            	    name: RDB$RELATION_NAME
            	Field id: 5
            	    name: RDB$FIELD_NAME
            	Field id: 6
            	    name: RDB$USER_TYPE
            	Field id: 7
            	    name: RDB$OBJECT_TYPE
            	    trigger_name: RDB$TRIGGER_1
            	    trigger_name: RDB$TRIGGER_8
            	    trigger_name: RDB$TRIGGER_9
            	    trigger_name: RDB$TRIGGER_31
            	    trigger_name: RDB$TRIGGER_32
            	    trigger_name: RDB$TRIGGER_33

    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 7
    RDB$RELATION_NAME               RDB$VIEW_RELATIONS                                                                                                                                                                                                                                          
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    6
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               0
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 48
    RDB$RELATION_NAME               SEC$DB_CREATORS                                                                                                                                                                                                                                             
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    2
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 46
    RDB$RELATION_NAME               SEC$GLOBAL_AUTH_MAPPING                                                                                                                                                                                                                                     
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 43
    RDB$RELATION_NAME               SEC$USERS                                                                                                                                                                                                                                                   
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    8
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>

    RDB$RELATION_ID                 44
    RDB$RELATION_NAME               SEC$USER_ATTRIBUTES                                                                                                                                                                                                                                         
    RDB$SYSTEM_FLAG                 1
    RDB$DBKEY_LENGTH                8
    RDB$FORMAT                      0
    RDB$FIELD_ID                    4
    RDB$FLAGS                       <null>
    RDB$RELATION_TYPE               3
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$EXTERNAL_FILE               <null>
    VIEW_BLR_BLOB_ID                <null>
    VIEW_SRC_BLOB_ID                <null>
    DESCR_BLOB_ID                   <null>
    RUNTIME_BLOB_ID                 <null>
    EXT_DESCR_BLOB_ID               <null>


    Records affected: 54
  """

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

