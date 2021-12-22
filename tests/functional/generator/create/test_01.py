#coding:utf-8
#
# id:           functional.generator.create.01
# title:        Run CREATE GENERATOR and query related data from RDB$GENERATORS.
# decription:   
#                  Run 'CREATE GENERATOR' statement and obtain data about it from system table (rdb$generators).
#                  07-aug-2020: we have to separate test for 3.0 and 4.0 because INITIAL value of new sequence
#                  in FB 4.x now differs from "old good zero" (this is so since CORE-6084 was fixed).
#               
#                  See also: doc/README.incompatibilities.3to4.txt
#                
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.generator.create.create_generator_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('RDB\\$SECURITY_CLASS[ ]+SQL\\$.*', ''), ('RDB\\$GENERATOR_ID.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create generator test;
    commit;
    set list on;
    select * from rdb$generators where rdb$generator_name=upper('test');  
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$GENERATOR_NAME              TEST
    RDB$GENERATOR_ID                12
    RDB$SYSTEM_FLAG                 0
    RDB$DESCRIPTION                 <null>
    RDB$SECURITY_CLASS              SQL$366
    RDB$OWNER_NAME                  SYSDBA
    RDB$INITIAL_VALUE               0
    RDB$GENERATOR_INCREMENT         1
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = [('RDB\\$SECURITY_CLASS[ ]+SQL\\$.*', ''), ('RDB\\$GENERATOR_ID.*', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    create generator test;
    commit;
    set list on;
    select * from rdb$generators where rdb$generator_name=upper('test');  
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$GENERATOR_NAME              TEST
    RDB$GENERATOR_ID                12
    RDB$SYSTEM_FLAG                 0
    RDB$DESCRIPTION                 <null>
    RDB$SECURITY_CLASS              SQL$366
    RDB$OWNER_NAME                  SYSDBA
    RDB$INITIAL_VALUE               1
    RDB$GENERATOR_INCREMENT         1
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

