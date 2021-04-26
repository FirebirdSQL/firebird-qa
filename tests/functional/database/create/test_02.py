#coding:utf-8
#
# id:           functional.database.create_02
# title:        CREATE DATABASE - non sysdba user
# decription:   
# tracker_id:   
# min_versions: ['2.1.7']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set bail on;
    create or alter user ozzy password 'osb' revoke admin role;
    commit;
    revoke all on all from ozzy;
    commit;

    --  ::: NB ::: do NOT miss specification of 'USER' or 'ROLE' clause in
    --  GRANT | REVOKE CREATE DATABASE, between `to` and login! Otherwise:
    --    Statement failed, SQLSTATE = 0A000
    --    unsuccessful metadata update
    --    -GRANT failed
    --    -feature is not supported
    --    -Only grants to USER or ROLE are supported for CREATE DATABASE
    grant create database to USER ozzy;
    --                       ^^^^
    grant drop database to USER ozzy;
    --                     ^^^^
    commit;
    
    create database 'localhost:$(DATABASE_LOCATION)tmp.ozzy$db$987456321.tmp' user 'OZZY' password 'osb';
    
    set list on;
    select
         a.mon$user "Who am I ?"
        ,iif( m.mon$database_name containing 'tmp.ozzy$db$987456321.tmp' , 'YES', 'NO! ' || m.mon$database_name) "Am I on just created DB ?"
    from mon$database m, mon$attachments a where a.mon$attachment_id = current_connection;
    commit;
    
    drop database;
    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    revoke create database from user ozzy;
    revoke drop database from user ozzy;
    drop user ozzy;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Who am I ?                      OZZY
    Am I on just created DB ?       YES
  """

@pytest.mark.version('>=3.0')
def test_create_02_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

