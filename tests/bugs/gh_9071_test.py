#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9071
TITLE:       Support for DROP SCHEMA CASCADE
DESCRIPTION:
    Test creates three schemas.
    Two of them have cyclic dependencies and thus may not be dropped; third has no dependent objects and shoudl be dropped w/o errors.
    After third schema is dropped, its name must not appear in the RDB$SCHEMAS table.
NOTES:
    [14.08.2026] pzotov
    Checked on 6.0.0.2147-6aadfe4
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

test_script = """
    set bail on;
    set list on;
    set autoterm on;
    --set autoddl off;
    create schema s_required;
    create schema s_optional;
    create schema s_old_junk;

    create table s_required.test(id int);
    create table s_optional.test(id int);
    create table s_old_junk.test(id int);

    create procedure sp_count as -- PUBLIC
        declare n int;
    begin
        select count(*) from s_optional.test into n;
    end;
    ----------------------------------------------
    create procedure s_required.sp_count as
        declare n int;
    begin
        select count(*) from s_optional.test into n;
    end;
    ----------------------------------------------
    create procedure s_optional.sp_count as
        declare n int;
    begin
        select count(*) from s_required.test into n;
    end;
    ----------------------------------------------
    create procedure s_old_junk.sp_count as
        declare n int;
    begin
        execute procedure s_required.sp_count; -- from ANOTHER schema.
    end;

    create procedure s_old_junk.sp_factorial(a_n smallint) returns(o_n int128) as
    begin
        if (a_n > 1) then
            select o_n from s_old_junk.sp_factorial(:a_n - 1) into o_n;
        else
            o_n = 1;
    end;
    ----------------------------------------------

    set bail off;
    drop schema s_required cascade; -- must FAIL: proc 's_optional.sp_count' depends on this schema
    drop schema s_optional cascade; -- must FAIL: proc 's_required.sp_count' depends on this schema
    drop schema s_old_junk cascade; -- must PASS
    commit;
    set count on;
    select rdb$schema_name from rdb$schemas where rdb$system_flag is distinct from 1 order by 1;

    -- must return zero rows:
    select rdb$relation_name from rdb$relations where rdb$schema_name = upper('s_old_junk');
    select rdb$procedure_name from rdb$procedures where rdb$schema_name = upper('s_old_junk');
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -DROP SCHEMA "S_REQUIRED" failed
    -cannot delete
    -there are 1 dependencies

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -DROP SCHEMA "S_OPTIONAL" failed
    -cannot delete
    -there are 1 dependencies

    RDB$SCHEMA_NAME PUBLIC
    RDB$SCHEMA_NAME S_OPTIONAL
    RDB$SCHEMA_NAME S_REQUIRED
    Records affected: 3

    Records affected: 0
    Records affected: 0
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
