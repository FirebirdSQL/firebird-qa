#coding:utf-8
"""
ID:          issue-7350
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7350
TITLE:       SKIP LOCKED clause for SELECT WITH LOCK, UPDATE and DELETE
DESCRIPTION: test verifies ability to get records from table which already has several locked rows by another transaction.
             Check performs for several type of queries:
                 1) DSQL 
                 2) PSQL which uses static SQL code
                 3) PSQL which uses ES/EDS mechanism.
             Two type of access mode is checked: READ and READ_WRITE
             All kinds of transaction isolation levels are involved: TABLE STABILITY; SNAPSHOT; RC READ_CONSISTENCY; RC REC_VER and RC NO_REC_VER.
NOTES:
    [27.02.2023] pzotov
    ::: NB :::
    1) Parameter ReadConsistency in firebird.conf must be set to 0, i.e. NOT-default value.
    2) Query that uses TIL = "RC NO_record_version" actually can not obtain any records, despite usage of SKIP LOCKED clause. It always fail with:
       "-read conflicts with concurrent update / -concurrent transaction number is ..."

    Checked on 5.0.0.959 SS/CS.
"""

import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, TraLockResolution, TraAccessMode, DatabaseError
import time

db = db_factory()
substitutions = [ ('transaction number is \\d+', 'transaction number is'),
                  ("-At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL' line.*", "-At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL'"),
                  ("-At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE' line.*", "-At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE'"),
                  ('Data source : Firebird::localhost:.*', 'Data source : Firebird::localhost:')
                ]
act = python_act('db', substitutions = substitutions)

CHECK_SQL = 'select id from test order by id rows 2 with lock skip locked'

expected_stdout = f"""
    QUERY_TYPE = DSQL, TIL = SERIALIZABLE, ACCESS = READ:
    lock conflict on no wait transaction
    -Acquire lock for relation (TEST) failed
    -901
    335544345
    335544382

    QUERY_TYPE = DSQL, TIL = SNAPSHOT, ACCESS = READ:
    attempted update during read-only transaction
    -817
    335544361

    QUERY_TYPE = DSQL, TIL = READ_COMMITTED_READ_CONSISTENCY, ACCESS = READ:
    attempted update during read-only transaction
    -817
    335544361

    QUERY_TYPE = DSQL, TIL = READ_COMMITTED_RECORD_VERSION, ACCESS = READ:
    attempted update during read-only transaction
    -817
    335544361

    QUERY_TYPE = DSQL, TIL = READ_COMMITTED_NO_RECORD_VERSION, ACCESS = READ:
    deadlock
    -read conflicts with concurrent update
    -concurrent transaction number is
    -913
    335544336
    335545096
    335544878

    QUERY_TYPE = DSQL, TIL = SERIALIZABLE, ACCESS = WRITE:
    lock conflict on no wait transaction
    -Acquire lock for relation (TEST) failed
    -901
    335544345
    335544382

    QUERY_TYPE = DSQL, TIL = SNAPSHOT, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = DSQL, TIL = READ_COMMITTED_READ_CONSISTENCY, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = DSQL, TIL = READ_COMMITTED_RECORD_VERSION, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = DSQL, TIL = READ_COMMITTED_NO_RECORD_VERSION, ACCESS = WRITE:
    deadlock
    -read conflicts with concurrent update
    -concurrent transaction number is
    -913
    335544336
    335545096
    335544878


    QUERY_TYPE = PSQL_LOCAL, TIL = SERIALIZABLE, ACCESS = READ:
    lock conflict on no wait transaction
    -Acquire lock for relation (TEST) failed
    -At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL' line: 3, col: 13
    -901
    335544345
    335544382
    335544842

    QUERY_TYPE = PSQL_LOCAL, TIL = SNAPSHOT, ACCESS = READ:
    attempted update during read-only transaction
    -At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL' line: 3, col: 13
    -817
    335544361
    335544842

    QUERY_TYPE = PSQL_LOCAL, TIL = READ_COMMITTED_READ_CONSISTENCY, ACCESS = READ:
    attempted update during read-only transaction
    -At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL' line: 3, col: 13
    -817
    335544361
    335544842

    QUERY_TYPE = PSQL_LOCAL, TIL = READ_COMMITTED_RECORD_VERSION, ACCESS = READ:
    attempted update during read-only transaction
    -At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL' line: 3, col: 13
    -817
    335544361
    335544842

    QUERY_TYPE = PSQL_LOCAL, TIL = READ_COMMITTED_NO_RECORD_VERSION, ACCESS = READ:
    deadlock
    -read conflicts with concurrent update
    -concurrent transaction number is
    -At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL' line: 3, col: 13
    -913
    335544336
    335545096
    335544878
    335544842

    QUERY_TYPE = PSQL_LOCAL, TIL = SERIALIZABLE, ACCESS = WRITE:
    lock conflict on no wait transaction
    -Acquire lock for relation (TEST) failed
    -At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL' line: 3, col: 13
    -901
    335544345
    335544382
    335544842

    QUERY_TYPE = PSQL_LOCAL, TIL = SNAPSHOT, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = PSQL_LOCAL, TIL = READ_COMMITTED_READ_CONSISTENCY, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = PSQL_LOCAL, TIL = READ_COMMITTED_RECORD_VERSION, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = PSQL_LOCAL, TIL = READ_COMMITTED_NO_RECORD_VERSION, ACCESS = WRITE:
    deadlock
    -read conflicts with concurrent update
    -concurrent transaction number is
    -At procedure 'SP_GET_UNLOCKED_ROWS_LOCAL' line: 3, col: 13
    -913
    335544336
    335545096
    335544878
    335544842


    QUERY_TYPE = PSQL_REMOTE, TIL = SERIALIZABLE, ACCESS = READ:
    Execute statement error at isc_dsql_fetch :
    335544345 : lock conflict on no wait transaction
    335544382 : Acquire lock for relation (TEST) failed
    Statement : {CHECK_SQL}
    Data source : Firebird::localhost:C:/TEMP/PYTEST/TEST_nnn/TEST.FDB
    -At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE' line: 3, col: 13
    -901
    335544926
    335544842

    QUERY_TYPE = PSQL_REMOTE, TIL = SNAPSHOT, ACCESS = READ:
    Execute statement error at isc_dsql_fetch :
    335544361 : attempted update during read-only transaction
    Statement : {CHECK_SQL}
    Data source : Firebird::localhost:C:/TEMP/PYTEST/TEST_nnn/TEST.FDB
    -At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE' line: 3, col: 13
    -901
    335544926
    335544842

    QUERY_TYPE = PSQL_REMOTE, TIL = READ_COMMITTED_READ_CONSISTENCY, ACCESS = READ:
    Execute statement error at isc_dsql_fetch :
    335544361 : attempted update during read-only transaction
    Statement : {CHECK_SQL}
    Data source : Firebird::localhost:C:/TEMP/PYTEST/TEST_nnn/TEST.FDB
    -At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE' line: 3, col: 13
    -901
    335544926
    335544842

    QUERY_TYPE = PSQL_REMOTE, TIL = READ_COMMITTED_RECORD_VERSION, ACCESS = READ:
    Execute statement error at isc_dsql_fetch :
    335544361 : attempted update during read-only transaction
    Statement : {CHECK_SQL}
    Data source : Firebird::localhost:C:/TEMP/PYTEST/TEST_nnn/TEST.FDB
    -At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE' line: 3, col: 13
    -901
    335544926
    335544842

    QUERY_TYPE = PSQL_REMOTE, TIL = READ_COMMITTED_NO_RECORD_VERSION, ACCESS = READ:
    Execute statement error at isc_dsql_fetch :
    335544336 : deadlock
    335545096 : read conflicts with concurrent update
    335544878 : concurrent transaction number is
    Statement : {CHECK_SQL}
    Data source : Firebird::localhost:C:/TEMP/PYTEST/TEST_nnn/TEST.FDB
    -At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE' line: 3, col: 13
    -901
    335544926
    335544842

    QUERY_TYPE = PSQL_REMOTE, TIL = SERIALIZABLE, ACCESS = WRITE:
    Execute statement error at isc_dsql_fetch :
    335544345 : lock conflict on no wait transaction
    335544382 : Acquire lock for relation (TEST) failed
    Statement : {CHECK_SQL}
    Data source : Firebird::localhost:C:/TEMP/PYTEST/TEST_nnn/TEST.FDB
    -At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE' line: 3, col: 13
    -901
    335544926
    335544842

    QUERY_TYPE = PSQL_REMOTE, TIL = SNAPSHOT, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = PSQL_REMOTE, TIL = READ_COMMITTED_READ_CONSISTENCY, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = PSQL_REMOTE, TIL = READ_COMMITTED_RECORD_VERSION, ACCESS = WRITE:
    ID=2
    ID=3

    QUERY_TYPE = PSQL_REMOTE, TIL = READ_COMMITTED_NO_RECORD_VERSION, ACCESS = WRITE:
    Execute statement error at isc_dsql_fetch :
    335544336 : deadlock
    335545096 : read conflicts with concurrent update
    335544878 : concurrent transaction number is
    Statement : {CHECK_SQL}
    Data source : Firebird::localhost:C:/TEMP/PYTEST/TEST_nnn/TEST.FDB
    -At procedure 'SP_GET_UNLOCKED_ROWS_REMOTE' line: 3, col: 13
    -901
    335544926
    335544842
"""
@pytest.mark.version('>=5.0')
def test_1(act: Action, capsys):

    init_sql = f"""
        set term ^;
        recreate table test(id int primary key, f01 int)
        ^
        create or alter procedure sp_get_unlocked_rows_local returns(id int) as
        begin
            for
                {CHECK_SQL}
                into id
            do
                suspend;
        end
        ^
        create or alter procedure sp_get_unlocked_rows_remote returns(id int) as
        begin
            for
                execute statement '{CHECK_SQL}'
                on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
                as user '{act.db.user}' password '{act.db.password}'
                into id
            do
                suspend;
        end
        ^
        set term ^;
        commit;

        insert into test(id, f01) select row_number()over(), 0 from rdb$types rows 10;
        commit;
    """ 
    act.isql(switches=['-q'], input = init_sql, combine_output = True)
    assert act.clean_stdout == ''
    act.reset()

    tpb_isol_set = (Isolation.SERIALIZABLE, Isolation.SNAPSHOT, Isolation.READ_COMMITTED_READ_CONSISTENCY, Isolation.READ_COMMITTED_RECORD_VERSION, Isolation.READ_COMMITTED_NO_RECORD_VERSION)
    tpb_wait_set = (TraLockResolution.NO_WAIT,) # TraLockResolution.WAIT,
    tpb_mode_set = (TraAccessMode.READ, TraAccessMode.WRITE)

    with act.db.connect() as con_rows_locker, act.db.connect() as con_free_seeker:
        con_rows_locker.execute_immediate('update test set f01 = 1 where id in (1,5,9)')

        for query_type in ('DSQL', 'PSQL_LOCAL', 'PSQL_REMOTE'):
            for x_mode in tpb_mode_set:
                for x_isol in tpb_isol_set:
                    custom_tpb = tpb(isolation = x_isol, access_mode = x_mode, lock_timeout = 0)
                    #custom_tpb = TPB(isolation = x_isol, access_mode = x_mode, lock_timeout = 0).get_buffer()
                    tx_free_seeker = con_free_seeker.transaction_manager(custom_tpb)
                    cur_free_seeker = tx_free_seeker.cursor()
                    tx_free_seeker.begin()
                    try:
                        print('\n')
                        print(f'QUERY_TYPE = {query_type}, TIL = {x_isol.name}, ACCESS = {x_mode.name}:')
                        if query_type == 'DSQL':
                            cur_free_seeker.execute(f'{CHECK_SQL}')
                        elif query_type == 'PSQL_LOCAL':
                            cur_free_seeker.execute('select id from sp_get_unlocked_rows_local')
                        elif query_type == 'PSQL_REMOTE':
                            cur_free_seeker.execute('select id from sp_get_unlocked_rows_remote')
                        for r in cur_free_seeker:
                             print('ID='+str(r[0]))
                    except DatabaseError as e:
                        print(e.__str__())
                        print(e.sqlcode)
                        for g in e.gds_codes:
                            print(g)
                    finally:
                        tx_free_seeker.rollback()

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
