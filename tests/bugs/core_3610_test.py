#coding:utf-8
#
# id:           bugs.core_3610
# title:        Can insert DUPLICATE keys in UNIQUE index
# decription:   
#                   Checked on:
#                       4.0.0.1635 SS: 1.368s.
#                       4.0.0.1633 CS: 2.094s.
#                       3.0.5.33180 SS: 0.907s.
#                       3.0.5.33178 CS: 1.345s.
#                       2.5.9.27119 SS: 0.299s.
#                       2.5.9.27146 SC: 0.294s.
#                
# tracker_id:   CORE-3610
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = [('Data source : Firebird::localhost:.*', 'Data source : Firebird::localhost:'), ('335544382 : Problematic key', '335545072 : Problematic key'), ('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    F01                             1
    ID                              2
    F01                             <null>
    ID                              3
    F01                             <null>
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_execute2 :
    335544665 : violation of PRIMARY or UNIQUE KEY constraint "TEST_UNQ" on table "TEST"
    335545072 : Problematic key value is ("F01" = 1)
    Statement : update test set f01 = ? where id = ?
    Data source : Firebird::localhost:
    -At block line: 3, col: 9
"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

