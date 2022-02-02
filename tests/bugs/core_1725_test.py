#coding:utf-8

"""
ID:          issue-2149
ISSUE:       2149
TITLE:       Unable to restore a database with inactive indices if any SP/trigger contains an explicit plan
DESCRIPTION:
JIRA:        CORE-1725
FBTEST:      bugs.core_1725
"""

import pytest
from firebird.qa import *
from firebird.driver import SrvRestoreFlag, SrvRepairFlag
from io import BytesIO
from difflib import unified_diff

substitutions_1 = [('[ \t]+', ' ')]

init_script = """
set bail on;

create or alter procedure sp_init as begin end;
create or alter procedure sp_main as begin end;
create or alter procedure sp_worker as begin end;

create or alter function fn_init returns int as begin end;
create or alter function fn_main returns int as begin end;
create or alter function fn_worker returns int as begin end;


create table test(id int primary key, x int, y int);
create index test_x on test(x);
create descending index test_y on test(y);
commit;

insert into test(id, x, y) select row_number()over(), rand()*5, rand()*100 from rdb$types;
commit;

create or alter view v_init as
    select count(*) as cnt from test group by x
    rows 1
;

create or alter view v_worker as
    select count(*) as cnt
    from test
    group by y
    plan (TEST ORDER TEST_Y)
    union all
    select cnt from v_init
;
commit;


set term ^;
execute block as
begin
    rdb$set_context('USER_SESSION','INITIAL_DDL', '1');
end
^

create or alter procedure sp_init as
    declare c int;
begin
    select count(*) from test group by x
    rows 1
    into c
    ;
end
^

create or alter procedure sp_main as
begin
    execute procedure sp_worker;
end
^

create or alter procedure sp_worker as
    declare c int;
begin
    select sum(cnt)
    from (
        select count(*) as cnt
        from test group by x
        plan (TEST ORDER TEST_X)
        union all
        select cnt from v_worker
    )
    into c
    ;
end
^
create or alter function fn_init returns int as
begin
    return ( select count(*) from test );
end
^
create or alter function fn_worker returns int as
begin
    return (
        select sum(cnt)
        from (
            select count(*) as cnt
            from test group by x
            plan (TEST ORDER TEST_X)
            union all
            select cnt from v_worker
        )
    );
end
^
create or alter function fn_main returns int as
begin
    return fn_worker();
end
^

create or alter package pg_test as
begin
    function pg_fn_worker returns int;
    procedure pg_sp_worker;
end
^
recreate package body pg_test as
begin
    function pg_fn_worker returns int as
    begin
        return (
            select sum(cnt)
            from (
                select count(*) as cnt
                from test group by x
                plan (TEST ORDER TEST_X)
                union all
                select cnt from v_worker
            )
        );
    end

    procedure pg_sp_worker as
        declare c int;
    begin
        select sum(cnt)
        from (
            select count(*) as cnt
            from test group by x
            plan (TEST ORDER TEST_X)
            union all
            select cnt from v_worker
        )
        into c
        ;
    end

end
^

create or alter trigger trg_attach active on connect position 0 as
    declare c int;
begin
    if ( rdb$get_context('USER_SESSION','INITIAL_DDL') is null ) then
    begin
        select sum(cnt)
        from (
            select count(*) as cnt
            from test group by x
            plan (TEST ORDER TEST_X)
            union all
            select cnt from v_worker
        )
        into c;
    end
end
^
set term ;^
commit;
"""

db = db_factory(init=init_script)

act = python_act('db')

@pytest.mark.version('>=3.0.6')
def test_1(act: Action):
    # Extract metadata from initial DB
    act.isql(switches=['-nod', '-x'])
    meta_1 = act.stdout
    act.reset()
    # backup  + restore _WITHOUT_ building indices:
    backup = BytesIO()
    with act.connect_server() as srv:
        srv.database.local_backup(database=act.db.db_path, backup_stream=backup)
        backup.seek(0)
        srv.database.local_restore(backup_stream=backup, database=act.db.db_path,
                                   flags=SrvRestoreFlag.DEACTIVATE_IDX | SrvRestoreFlag.REPLACE)
        # Get FB log before validation, run validation and get FB log after it:
        log_before = act.get_firebird_log()
        srv.database.repair(database=act.db.db_path, flags=SrvRepairFlag.CORRUPTION_CHECK)
        #act.gfix(switches=['-v', '-full', act.db.dsn])
        log_after = act.get_firebird_log()
    # Extract metadata from restored DB
    act.isql(switches=['-nod', '-x'])
    meta_2 = act.stdout
    act.reset()
    # Restore with indices. This is necessary to drop the database safely otherwise connect
    # to drop will fail in test treadown as connect trigger referes to index tat was not activated
    with act.connect_server() as srv:
        backup.seek(0)
        srv.database.local_restore(backup_stream=backup, database=act.db.db_path,
                                   flags=SrvRestoreFlag.REPLACE)
    #
    diff_meta = ''.join(unified_diff(meta_1.splitlines(), meta_2.splitlines()))
    diff_log = [line for line in unified_diff(log_before, log_after) if line.startswith('+') and 'Validation finished:' in line]
    # Checks
    assert diff_meta == ''
    assert diff_log == ['+\tValidation finished: 0 errors, 0 warnings, 0 fixed\n']
