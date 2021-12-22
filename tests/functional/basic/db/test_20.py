#coding:utf-8
#
# id:           functional.basic.db.20
# title:        New database: content of RDB$PROCEDURES
# decription:   
#                  Check for correct content of RDB$PROCEDURES in a new database.
#                  15.01.2019. Split 'firebird_version' because 4.0 now has SP in new database.
#                
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_20

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
     set count on; 
     set list on;
     set blob all; 
     select p.* 
     from rdb$procedures p
     order by p.rdb$procedure_id;
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
     set count on; 
     set list on;
     set blob all; 
     select p.* 
     from rdb$procedures p
     order by p.rdb$procedure_id;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$PROCEDURE_NAME              TRANSITIONS                                                                                                                                                                                                                                                 
    RDB$PROCEDURE_ID                1
    RDB$PROCEDURE_INPUTS            3
    RDB$PROCEDURE_OUTPUTS           5
    RDB$DESCRIPTION                 <null>
    RDB$PROCEDURE_SOURCE            <null>
    RDB$PROCEDURE_BLR               <null>
    RDB$SECURITY_CLASS              <null>
    RDB$OWNER_NAME                  SYSDBA                                                                                                                                                                                                                                                      
    RDB$RUNTIME                     <null>
    RDB$SYSTEM_FLAG                 1
    RDB$PROCEDURE_TYPE              1
    RDB$VALID_BLR                   1
    RDB$DEBUG_INFO                  <null>
    RDB$ENGINE_NAME                 SYSTEM                                                                                                                                                                                                                                                      
    RDB$ENTRYPOINT                  <null>
    RDB$PACKAGE_NAME                RDB$TIME_ZONE_UTIL                                                                                                                                                                                                                                          
    RDB$PRIVATE_FLAG                0
    RDB$SQL_SECURITY                <null>

    Records affected: 1
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

