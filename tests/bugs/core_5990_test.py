#coding:utf-8
#
# id:           bugs.core_5990
# title:        Pool of external connections
# decription:
#                   Test assumes that firebird.conf contains:
#                     ExtConnPoolSize = 100 (or at any other value >= 6)
#                     ExtConnPoolLifeTime = 10
#                   We run six execute blocks with COMMIT after each of them.
#                   When EDS pool is enabled then every new execute block will use the same attachment as it was established in the 1st EB.
#                   We check this by running query that show number of duplicates for each of N attachments: this number must be equal to N-1.
#                   ::: NB :::
#                   Final statement must be 'ALTER EXTERNAL CONNECTIONS POOL CLEAR ALL' otherwise DB file will be kept by engine at least
#                   for 10 seconds after this test finish (see parameter 'ExtConnPoolLifeTime').
#
#                   Thank hvlad for additional explanations, discuss in e-mail was 26.04.19 09:38.
#
#                   Checked on 4.0.0.1501 (both SS and CS): OK, 1.343s.
#
# tracker_id:   CORE-5990
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate view v_conn as
    select
        cast(rdb$get_context('SYSTEM', 'EXT_CONN_POOL_SIZE') as int) as pool_size,
        cast(rdb$get_context('SYSTEM', 'EXT_CONN_POOL_IDLE_COUNT') as int) as pool_idle,
        cast(rdb$get_context('SYSTEM', 'EXT_CONN_POOL_ACTIVE_COUNT') as int) as pool_active,
        cast(rdb$get_context('SYSTEM', 'EXT_CONN_POOL_LIFETIME') as int) as pool_lifetime
    from rdb$database
    ;

    create sequence g;
    commit;

    recreate table att_info(id int, established_attach_id int);
    commit;

    set term ^;
    execute block as
    begin
        rdb$set_context('USER_SESSION', 'DBA_USER', 'SYSDBA');
        rdb$set_context('USER_SESSION', 'DBA_PSWD', 'masterkey');
    end
    ^

    execute block as
        declare con1 int;
    begin
        execute statement 'select current_connection from rdb$database'
            on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
            as user rdb$get_context('USER_SESSION', 'DBA_USER') password rdb$get_context('USER_SESSION', 'DBA_PSWD')
        into con1;
        insert into att_info(id, established_attach_id) values( gen_id(g,1), :con1 );

    end
    ^
    commit -- <<< NOTA BENE <<<<  C.O.M.M.I.T after each execute block <<<
    ^

    execute block as
        declare con1 int;
    begin
        execute statement 'select current_connection from rdb$database'
            on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
            as user rdb$get_context('USER_SESSION', 'DBA_USER') password rdb$get_context('USER_SESSION', 'DBA_PSWD')
        into con1;
        insert into att_info(id, established_attach_id) values( gen_id(g,1), :con1 );

    end
    ^
    commit
    ^

    execute block as
        declare con1 int;
    begin
        execute statement 'select current_connection from rdb$database'
            on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
            as user rdb$get_context('USER_SESSION', 'DBA_USER') password rdb$get_context('USER_SESSION', 'DBA_PSWD')
        into con1;
        insert into att_info(id, established_attach_id) values( gen_id(g,1), :con1 );

    end
    ^
    commit
    ^

    execute block as
        declare con1 int;
    begin
        execute statement 'select current_connection from rdb$database'
            on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
            as user rdb$get_context('USER_SESSION', 'DBA_USER') password rdb$get_context('USER_SESSION', 'DBA_PSWD')
        into con1;
        insert into att_info(id, established_attach_id) values( gen_id(g,1), :con1 );

    end
    ^
    commit
    ^

    execute block as
        declare con1 int;
    begin
        execute statement 'select current_connection from rdb$database'
            on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
            as user rdb$get_context('USER_SESSION', 'DBA_USER') password rdb$get_context('USER_SESSION', 'DBA_PSWD')
        into con1;
        insert into att_info(id, established_attach_id) values( gen_id(g,1), :con1 );

    end
    ^
    commit
    ^

    execute block as
        declare con1 int;
    begin
        execute statement 'select current_connection from rdb$database'
            on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
            as user rdb$get_context('USER_SESSION', 'DBA_USER') password rdb$get_context('USER_SESSION', 'DBA_PSWD')
        into con1;
        insert into att_info(id, established_attach_id) values( gen_id(g,1), :con1 );

    end
    ^
    commit
    ^
    set term ;^

    --set echo on;
    --select * from v_conn;
    --select a.id, a.established_attach_id, count(*)over(partition by established_attach_id)-1 dup_cnt

    set list on;
    select a.id, count(*)over(partition by established_attach_id)-1 dup_cnt
    from att_info a
    order by id;

    ALTER EXTERNAL CONNECTIONS POOL CLEAR ALL; -- !! mandatory otherwise database file will be kept by engine and fbtest will not able to drop it !!
    commit;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    DUP_CNT                         5
    ID                              2
    DUP_CNT                         5
    ID                              3
    DUP_CNT                         5
    ID                              4
    DUP_CNT                         5
    ID                              5
    DUP_CNT                         5
    ID                              6
    DUP_CNT                         5
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

