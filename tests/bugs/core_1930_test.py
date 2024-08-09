#coding:utf-8

"""
ID:          issue-2365
ISSUE:       2365
TITLE:       Possible AV in engine if procedure was altered to have no outputs and dependent procedures was not recompiled
DESCRIPTION:
JIRA:        CORE-1930
FBTEST:      bugs.core_1930
"""

import pytest
from firebird.qa import *

substitutions = [('Data source : Firebird::localhost:.*', 'Data source : Firebird::localhost:'),
                 ('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

db = db_factory()

# version: 3.0

test_script_1 = """
    set term ^;
    create or alter procedure sp1 returns (x int) as
    begin
        x=1;
        suspend;
    end
    ^

    create or alter procedure sp2 returns (x int) as
    begin
        select x from sp1 into :x;
        suspend;
    end
    ^

    create or alter procedure sp3 returns (x int)  as
    begin
        select x from sp2 into :x;
        suspend;
    end
    ^
    commit
    ^

    -- this is wrong but engine still didn't track procedure's fields dependencies
    create or alter procedure sp1 as
    begin
        exit;
    end
    ^

    set term ;^
    commit;

    -- Here we create new attachment using specification of some non-null data in ROLE clause:
    set term ^;
    execute block as
        declare c int;
    begin
        begin
            c = rdb$get_context('SYSTEM', 'EXT_CONN_POOL_SIZE');
            rdb$set_context('USER_SESSION', 'EXT_CONN_POOL_SUPPORT','1');
        when any do
            begin
            end
        end
        execute statement 'create or alter procedure sp3 as begin  execute procedure sp2; end'
        on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
        as user 'sysdba' password 'masterkey' role 'R1930';
    end
    ^
    commit
    ^

    --                                    ||||||||||||||||||||||||||||
    -- ###################################|||  HQBird 3.x  SS/SC   |||##############################
    --                                    ||||||||||||||||||||||||||||
    -- If we check SS or SC and ExtConnPoolLifeTime > 0 (avaliable in HQbird 3.x) then current
    -- DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
    -- will not able to drop this database at the final point of test.
    -- Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
    -- we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
    -- in the letter to hvlad and dimitr 13.10.2019 11:10).
    -- This means that one need to kill all connections to prevent from exception on cleanup phase:
    -- SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
    -- #############################################################################################
    execute block as
    begin
        if ( rdb$get_context('USER_SESSION', 'EXT_CONN_POOL_SUPPORT') = '1' ) then
        begin
            -- HQbird is tested now:
            -- execute statement 'delete from mon$attachments where mon$attachment_id != current_connection';
            execute statement 'ALTER EXTERNAL CONNECTIONS POOL CLEAR ALL';
        end
    end
    ^
    commit
    ^
"""

act_1 = isql_act('db', test_script_1, substitutions=substitutions)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_execute2 :
    335544351 : unsuccessful metadata update
    336397267 : CREATE OR ALTER PROCEDURE SP3 failed
    335544569 : Dynamic SQL Error
    335544850 : Output parameter mismatch for procedure SP2
    Statement : create or alter procedure sp3 as begin  execute procedure sp2; end
    Data source : Firebird::localhost:C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\C1930.FDB
    -At block line: 3, col: 9
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

# version: 4.0

test_script_2 = """
    set term ^;
    create or alter procedure sp1 returns (x int) as
    begin
      x=1;
      suspend;
    end
    ^

    create or alter procedure sp2 returns (x int) as
    begin
      select x from sp1 into :x;
      suspend;
    end
    ^

    create or alter procedure sp3 returns (x int)  as
    begin
      select x from sp2 into :x;
      suspend;
    end
    ^

    commit
    ^


    -- this is wrong but engine still didn't track procedure's fields dependencies
    create or alter procedure sp1
    as
    begin
      exit;
    end
    ^

    set term ;^
    commit;

    -- Here we create new attachment using specification of some non-null data in ROLE clause:
    set term ^;
    execute block as
    begin
        execute statement 'create or alter procedure sp3 as begin  execute procedure sp2; end'
        on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
        as user 'sysdba' password 'masterkey' role 'R1930';
    end
    ^
    set term ;^
    commit;

    --                                    ||||||||||||||||||||||||||||
    -- ###################################|||  FB 4.0+, SS and SC  |||##############################
    --                                    ||||||||||||||||||||||||||||
    -- If we check SS or SC and ExtConnPoolLifeTime > 0 (config parameter FB 4.0+) then current
    -- DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
    -- will not able to drop this database at the final point of test.
    -- Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
    -- we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
    -- in the letter to hvlad and dimitr 13.10.2019 11:10).
    -- This means that one need to kill all connections to prevent from exception on cleanup phase:
    -- SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
    -- #############################################################################################

    delete from mon$attachments where mon$attachment_id != current_connection;
    commit;
"""

act_2 = isql_act('db', test_script_2, substitutions=substitutions)

expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -PARAMETER SP1.X
    -there are 1 dependencies

    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_execute2 :
    335544351 : unsuccessful metadata update
    336397267 : CREATE OR ALTER PROCEDURE SP3 failed
    335544569 : Dynamic SQL Error
    335544850 : Output parameter mismatch for procedure SP2
    Statement : create or alter procedure sp3 as begin  execute procedure sp2; end
    Data source : Firebird::localhost:
    -At block line
"""

@pytest.mark.es_eds
@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_stderr == act_2.clean_expected_stderr

