#coding:utf-8

"""
ID:          create-database-02
TITLE:       Create database: non sysdba user
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    Who am I ?                      OZZY
    Am I on just created DB ?       YES
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
