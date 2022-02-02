#coding:utf-8

"""
ID:          issue-3964
ISSUE:       3964
TITLE:       Can insert DUPLICATE keys in UNIQUE index
DESCRIPTION:
JIRA:        CORE-3610
FBTEST:      bugs.core_3610
"""

import pytest
from firebird.qa import *

substitutions = [('Data source : Firebird::localhost:.*', 'Data source : Firebird::localhost:'),
                 ('335544382 : Problematic key', '335545072 : Problematic key'),
                 ('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

db = db_factory()

test_script = """
    recreate table test(id int not null, f01 int, constraint test_unq unique(f01) using index test_unq);
    commit;
    insert into test values(1, 1 );
    insert into test values(2,null);
    insert into test values(3,null);
    commit;
    set transaction read committed record_version no wait;
    update test set f01=null where id=1;
    set term ^;
    execute block as
    begin
        execute statement ('update test set f01 = ? where id = ?') (1, 3)
        with autonomous transaction
        on external ( 'localhost:'||rdb$get_context('SYSTEM','DB_NAME') )
        as user 'sysdba' password 'masterkey' role 'role_02'
        ;
    end
    ^
    set term ;^
    rollback;

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

    set list on;
    select * from test;
"""

act = isql_act('db', test_script, substitutions=substitutions)

expected_stdout = """
    ID                              1
    F01                             1
    ID                              2
    F01                             <null>
    ID                              3
    F01                             <null>
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_execute2 :
    335544665 : violation of PRIMARY or UNIQUE KEY constraint "TEST_UNQ" on table "TEST"
    335545072 : Problematic key value is ("F01" = 1)
    Statement : update test set f01 = ? where id = ?
    Data source : Firebird::localhost:
    -At block line: 3, col: 9
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

