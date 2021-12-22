#coding:utf-8
#
# id:           bugs.core_1434
# title:        Incorrect result with EXECUTE STATEMENT and VARCHAR columns
# decription:   Last two bytes of VARCHAR columns are lost.
# tracker_id:   CORE-1434
# min_versions: []
# versions:     2.0.2
# qmid:         bugs.core_1434

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on; 
    set term ^;
    execute block returns (res varchar(31))
     as
     begin
        for execute statement
            'select cast(rdb$relation_name as varchar(24)) '
            || ' from rdb$relations r where r.rdb$system_flag = 1 and r.rdb$relation_name NOT starting with ''MON$'''
            || '  order by rdb$relation_id rows 30'
            into :res
        do
            suspend;
    end
    ^
    set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RES                             RDB$PAGES               
    RES                             RDB$DATABASE            
    RES                             RDB$FIELDS              
    RES                             RDB$INDEX_SEGMENTS      
    RES                             RDB$INDICES             
    RES                             RDB$RELATION_FIELDS     
    RES                             RDB$RELATIONS           
    RES                             RDB$VIEW_RELATIONS      
    RES                             RDB$FORMATS             
    RES                             RDB$SECURITY_CLASSES    
    RES                             RDB$FILES               
    RES                             RDB$TYPES               
    RES                             RDB$TRIGGERS            
    RES                             RDB$DEPENDENCIES        
    RES                             RDB$FUNCTIONS           
    RES                             RDB$FUNCTION_ARGUMENTS  
    RES                             RDB$FILTERS             
    RES                             RDB$TRIGGER_MESSAGES    
    RES                             RDB$USER_PRIVILEGES     
    RES                             RDB$TRANSACTIONS        
    RES                             RDB$GENERATORS          
    RES                             RDB$FIELD_DIMENSIONS    
    RES                             RDB$RELATION_CONSTRAINTS
    RES                             RDB$REF_CONSTRAINTS     
    RES                             RDB$CHECK_CONSTRAINTS   
    RES                             RDB$LOG_FILES           
    RES                             RDB$PROCEDURES          
    RES                             RDB$PROCEDURE_PARAMETERS
    RES                             RDB$CHARACTER_SETS      
    RES                             RDB$COLLATIONS          
"""

@pytest.mark.version('>=2.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

