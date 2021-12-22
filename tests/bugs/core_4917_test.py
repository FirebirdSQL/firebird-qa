#coding:utf-8
#
# id:           bugs.core_4917
# title:        ALTER DOMAIN ... TO <new_name> allows to specify <new_name> matching to 'RDB$[[:DIGIT:]]*'
# decription:   
# tracker_id:   CORE-4917
# min_versions: ['2.5.5']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- CREATION:
    -- #########
    
    -- First, check that direct creation of domain with 'RDB$' prefix is disabled:
    create domain rdb$1 int;
    
    -- This also should FAIL becase new domain name is written in UPPER case (despite quotes):
    create domain "RDB$2" int;
    
    -- This should pass because new though name starts with 'rdb$' it 
    -- is written in quotes and not in upper case:
    create domain "rdb$1" int;
    
    -- ALTERING:
    -- #########
    
    alter domain "rdb$1" to foo;
    
    alter domain foo to "rdb$1";
    
    -- This should pass because new though name starts with 'rdb$' it 
    -- is written in quotes and not in upper case:
    alter domain "rdb$1" to "rdb$2";
    
    -- this should FAIL:
    alter domain "rdb$2" to RDB$3;
    
    -- this also should FAIL becase new domain name is written in UPPER case (despite quotes):
    alter domain "rdb$2" to "RDB$3";
    
    show domain;
    
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    rdb$2
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE DOMAIN RDB$1 failed
    -SQL error code = -637
    -Implicit domain name RDB$1 not allowed in user created domain

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE DOMAIN RDB$2 failed
    -SQL error code = -637
    -Implicit domain name RDB$2 not allowed in user created domain

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER DOMAIN rdb$2 failed
    -SQL error code = -637
    -Implicit domain name RDB$3 not allowed in user created domain

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER DOMAIN rdb$2 failed
    -SQL error code = -637
    -Implicit domain name RDB$3 not allowed in user created domain
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

