#coding:utf-8
#
# id:           functional.basic.db.22
# title:        Empty DB - RDB$RELATION_CONSTRAINTS
# decription:   Check for correct content of RDB$RELATION_CONSTRAINTS in empty database.
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_22

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('RDB\\$CONSTRAINT_NAME[\\s]+RDB\\$INDEX.*', 'RDB\\$CONSTRAINT_NAME RDB\\$INDEX'), ('RDB\\$INDEX_NAME[\\s]+RDB\\$INDEX.*', 'RDB\\$INDEX_NAME RDB\\$INDEX')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select rc.*
    from rdb$relation_constraints rc
    order by lpad( trim(replace(rdb$constraint_name, 'RDB$INDEX_', '')),31,'0');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$CONSTRAINT_NAME             RDB$INDEX_0                                                                                  
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$RELATIONS                                                                                
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_0                                                                                  

    RDB$CONSTRAINT_NAME             RDB$INDEX_2                                                                                  
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FIELDS                                                                                   
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_2                                                                                  

    RDB$CONSTRAINT_NAME             RDB$INDEX_5                                                                                  
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$INDICES                                                                                  
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_5                                                                                  

    RDB$CONSTRAINT_NAME             RDB$INDEX_7                                                                                  
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$SECURITY_CLASSES                                                                         
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_7                                                                                  

    RDB$CONSTRAINT_NAME             RDB$INDEX_8                                                                                  
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$TRIGGERS                                                                                 
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_8                                                                                  

    RDB$CONSTRAINT_NAME             RDB$INDEX_9                                                                                  
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FUNCTIONS                                                                                
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_9                                                                                  

    RDB$CONSTRAINT_NAME             RDB$INDEX_11                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$GENERATORS                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_11                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_12                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$RELATION_CONSTRAINTS                                                                     
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_12                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_13                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$REF_CONSTRAINTS                                                                          
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_13                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_15                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$RELATION_FIELDS                                                                          
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_15                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_17                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FILTERS                                                                                  
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_17                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_18                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PROCEDURE_PARAMETERS                                                                     
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_18                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_19                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$CHARACTER_SETS                                                                           
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_19                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_20                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$COLLATIONS                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_20                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_21                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PROCEDURES                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_21                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_22                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PROCEDURES                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_22                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_23                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$EXCEPTIONS                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_23                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_24                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$EXCEPTIONS                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_24                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_25                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$CHARACTER_SETS                                                                           
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_25                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_26                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$COLLATIONS                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_26                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_32                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$TRANSACTIONS                                                                             
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_32                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_39                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$ROLES                                                                                    
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_39                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_44                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$BACKUP_HISTORY                                                                           
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_44                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_45                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FILTERS                                                                                  
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_45                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_46                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$GENERATORS                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_46                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_47                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PACKAGES                                                                                 
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_47                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_53                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FUNCTIONS                                                                                
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_53                                                                                 
    Records affected: 27
  """

@pytest.mark.version('>=3.0,<4.0')
def test_22_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('RDB\\$CONSTRAINT_NAME[\\s]+RDB\\$INDEX.*', 'RDB\\$CONSTRAINT_NAME RDB\\$INDEX'), ('RDB\\$INDEX_NAME[\\s]+RDB\\$INDEX.*', 'RDB\\$INDEX_NAME RDB\\$INDEX')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    set count on;
    select rc.*
    from rdb$relation_constraints rc
    order by lpad( trim(replace(rdb$constraint_name, 'RDB$INDEX_', '')),31,'0');
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$CONSTRAINT_NAME             RDB$INDEX_0                                                                                                                                                                                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$RELATIONS                                                                                                                                                                                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_0                                                                                                                                                                                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_2                                                                                                                                                                                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FIELDS                                                                                                                                                                                                                                                  
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_2                                                                                                                                                                                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_5                                                                                                                                                                                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$INDICES                                                                                                                                                                                                                                                 
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_5                                                                                                                                                                                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_7                                                                                                                                                                                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$SECURITY_CLASSES                                                                                                                                                                                                                                        
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_7                                                                                                                                                                                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_8                                                                                                                                                                                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$TRIGGERS                                                                                                                                                                                                                                                
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_8                                                                                                                                                                                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_9                                                                                                                                                                                                                                                 
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FUNCTIONS                                                                                                                                                                                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_9                                                                                                                                                                                                                                                 

    RDB$CONSTRAINT_NAME             RDB$INDEX_11                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$GENERATORS                                                                                                                                                                                                                                              
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_11                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_12                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$RELATION_CONSTRAINTS                                                                                                                                                                                                                                    
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_12                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_13                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$REF_CONSTRAINTS                                                                                                                                                                                                                                         
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_13                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_15                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$RELATION_FIELDS                                                                                                                                                                                                                                         
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_15                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_17                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FILTERS                                                                                                                                                                                                                                                 
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_17                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_18                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PROCEDURE_PARAMETERS                                                                                                                                                                                                                                    
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_18                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_19                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$CHARACTER_SETS                                                                                                                                                                                                                                          
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_19                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_20                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$COLLATIONS                                                                                                                                                                                                                                              
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_20                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_21                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PROCEDURES                                                                                                                                                                                                                                              
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_21                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_22                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PROCEDURES                                                                                                                                                                                                                                              
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_22                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_23                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$EXCEPTIONS                                                                                                                                                                                                                                              
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_23                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_24                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$EXCEPTIONS                                                                                                                                                                                                                                              
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_24                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_25                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$CHARACTER_SETS                                                                                                                                                                                                                                          
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_25                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_26                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$COLLATIONS                                                                                                                                                                                                                                              
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_26                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_32                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$TRANSACTIONS                                                                                                                                                                                                                                            
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_32                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_39                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$ROLES                                                                                                                                                                                                                                                   
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_39                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_44                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$BACKUP_HISTORY                                                                                                                                                                                                                                          
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_44                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_45                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FILTERS                                                                                                                                                                                                                                                 
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_45                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_46                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$GENERATORS                                                                                                                                                                                                                                              
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_46                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_47                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PACKAGES                                                                                                                                                                                                                                                
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_47                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_53                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$FUNCTIONS                                                                                                                                                                                                                                               
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_53                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_54                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$BACKUP_HISTORY                                                                                                                                                                                                                                          
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_54                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_55                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PUBLICATIONS                                                                                                                                                                                                                                            
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_55                                                                                                                                                                                                                                                

    RDB$CONSTRAINT_NAME             RDB$INDEX_56                                                                                                                                                                                                                                                
    RDB$CONSTRAINT_TYPE             UNIQUE     
    RDB$RELATION_NAME               RDB$PUBLICATION_TABLES                                                                                                                                                                                                                                      
    RDB$DEFERRABLE                  NO 
    RDB$INITIALLY_DEFERRED          NO 
    RDB$INDEX_NAME                  RDB$INDEX_56                                                                                                                                                                                                                                                


    Records affected: 30
  """

@pytest.mark.version('>=4.0')
def test_22_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

