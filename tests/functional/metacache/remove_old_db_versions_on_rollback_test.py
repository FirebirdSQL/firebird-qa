#coding:utf-8
"""
ID:          n/a
ISSUE:       n/a
TITLE:       ROLLBACK must clean metacache from previous version of DB objects: check result of change stored proc outcome arg to incompatible datatype.
DESCRIPTION:
    Before shared metacache introduction, ROLLBACK marked in the test script as "[ 1 ]" did not return stored proc out parameter
    to original datatype.
    Attempts to query table or view (that both depend of stored proc) failed with SQLSTATE = 22008 / data type not supported for arithmetic.
NOTES:
    [17.05.2026] pzotov
    Original letter to FB-team: 07.03.2026 0216.
    Important explanation from Vlad: 07.03.2026 0230 (metadata cache contained definition of old view).
    Additionally discussed with Alex, letters since 24.04.2026 1653; 11.05.2026 2001
    Checked on 6.0.0.1771-f73321c; 6.0.0.1954-352c429.
"""
import locale
import pytest
from firebird.qa import *

db = db_factory()
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_sql = f"""
        set list on;
        SET BAIL OFF;
        --###########
        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';
        
        -------------------------------   i n i t   ----------------------------------
        
        set term ^;
        create procedure sp_get_info returns(age int) as
        begin
            age = 1;
            suspend;
        end ^
        set term ;^
        commit;
         
        create view v_test as select sum(age) as age_total from sp_get_info;
         
        create table test(
            id int
           ,age_total computed by( (select sum(age) from sp_get_info) )
        );
        commit;
        insert into test(id) values(-1);
        commit;
         
        select 'point-1: proc' as msg, p.* from sp_get_info as p;
        select 'point-1: view' as msg, v.* from v_test v;
        select 'point-1: table' as msg, t.* from test t;
        commit;
         
        -------------------------------  a l t e r  ----------------------------------
         
        SET AUTODDL OFF;
         
        set term ^;
        alter procedure sp_get_info returns(at_moment time) as
        begin
            at_moment = '01:02:03.456';
            suspend;
        end ^
        set term ;^
        -- ! commented! -- commit;
         
        select 'point-2: proc' as msg, p.* from sp_get_info as p;
        select 'point-2: view' as msg, v.* from v_test v;
        select 'point-2: table' as msg, t.* from test t;

        select 'before attempt to commit' as msg from rdb$database;
        commit; -- must FAIL!
        select 'after attempt to commit' as msg from rdb$database;
         
        -- ############################################################
        -- ###  THIS MUST REMOVE OLD VERSION OF VIEW FROM METACACHE ###
        -- ############################################################
        -- Behaviour has changed since shared metacache intro (6.0.0.1771-f73321c):
        rollback; ------------------------------------------------------------ [ 1 ]

        select 'after rollback' as msg from rdb$database;
         
        select 'point-3: proc' as msg, p.* from sp_get_info as p;
        select 'point-3: view' as msg, v.* from v_test v;
        select 'point-3: table' as msg, t.* from test t;

        rollback;
        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';

        select 'after reconnect' as msg from rdb$database;
         
        select 'point-4: proc' as msg, p.* from sp_get_info as p;
        select 'point-4: view' as msg, v.* from v_test v;
        select 'point-4: table' as msg, t.* from test t;
    """
    
    act.expected_stdout = f"""
        MSG                             point-1: proc
        AGE                             1
        MSG                             point-1: view
        AGE_TOTAL                       1
        MSG                             point-1: table
        ID                              -1
        AGE_TOTAL                       1

        MSG                             point-2: proc
        AT_MOMENT                       01:02:03.4560

        Statement failed, SQLSTATE = 22008
        data type not supported for arithmetic
        
        Statement failed, SQLSTATE = 22008
        data type not supported for arithmetic
        
        MSG                             before attempt to commit

        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -cannot delete
        -PARAMETER "PUBLIC"."SP_GET_INFO".AGE
        -PARAMETER "PUBLIC"."SP_GET_INFO".AGE
        -there are 2 dependencies

        MSG                             after attempt to commit
        MSG                             after rollback

        MSG                             point-3: proc
        AGE                             1
        MSG                             point-3: view
        AGE_TOTAL                       1
        MSG                             point-3: table
        ID                              -1
        AGE_TOTAL                       1

        MSG                             after reconnect
        MSG                             point-4: proc
        AGE                             1
        MSG                             point-4: view
        AGE_TOTAL                       1
        MSG                             point-4: table
        ID                              -1
        AGE_TOTAL                       1
    """

    act.isql(switches = ['-q'], input = test_sql, combine_output = True, connect_db = False, credentials = False, charset = 'utf8', io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
