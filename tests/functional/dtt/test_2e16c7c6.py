#coding:utf-8

"""
ID:          https://github.com/FirebirdSQL/firebird/commit/2e16c7c6e79cba8492b3fe06093f1f228ffbf0e5
TITLE:       DECLARED TEMPORARY TABLE - fix problem with outer DLTT access in subroutine
DESCRIPTION:
NOTES:
    [07.08.2026] pzotov
    Discussed with dimitr, letters since 07.08.2026 1127.
    Problem was reproduced on dtt/test_dtt_subroutines_access.py but only in dev- build.
    The script in this test reproduces problem (crash) on regular snapshot.

    ::: NOTE :::
    Code may look odd: there is sub-routine 'inner_fn()' which is not called from anywhere,
    but such function *must* present here. Otherwise problem does not raise.
    Declaration block that causes problem is defined in 'declared_ddl'.
    It is checked on DB-level trigger, standalone and packaged units and execute block.
    All of them must compile fine.

    Confirmed bug on 6.0.0.2120-20c3375: FB crashes.
    Checked on 6.0.0.2120-2e16c7c.
"""
import time
import locale
from pathlib import Path
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' '), ('After line \\d+.*', '')]
act = python_act('db', substitutions = substitutions)
tmp_sql = temp_file('test_dtt_dml_statements.sql')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, capsys):

    declared_ddl = """
        declare local temporary table dtt_level_a (
            id int
        );

        declare procedure inner_sp(a_id int) as
            declare local temporary table dtt_level_b (
                id int
            );
        begin
            insert into dtt_level_a (id) values(:a_id);
            insert into dtt_level_b select * from dtt_level_a;
        end

        declare function inner_fn(a_id int) returns int as
        begin
            return 1;
        end
    """

    inner_sql = """
        execute procedure inner_sp(1)
    """

    ################
    ###  S Q L   ###
    ################
    ddl_full = f"""
        set bail on;
        set blob all;
        set list on;
        set autoterm on;
        set autoddl off;
        commit;

        create trigger trg_tx_commit on transaction commit as
            {declared_ddl}
        begin
            {inner_sql};
            rdb$set_context(
                'USER_SESSION',
                'DB_LEVEL_TRG',
                'OK'
            );
        end;

        create or alter procedure sp_test returns(out_result int) as
            {declared_ddl}
        begin
            {inner_sql};
            rdb$set_context(
                'USER_SESSION',
                'STANDALONE_PROC',
                'OK'
            );
            out_result = 1;
            suspend;
        end;

        ------------------------------
        create or alter function fn_test returns int as
            {declared_ddl}
        begin
            {inner_sql};
            rdb$set_context(
                'USER_SESSION',
                'STANDALONE_FUNC',
                'OK'
            );
            return 1;
        end;
        
        ------------------------------
        create or alter package pg_test as
        begin
            procedure pg_proc returns(out_result int);
            function pg_func() returns int;
        end;

        recreate package body pg_test as
        begin
            procedure pg_proc returns(out_result int) as
                {declared_ddl}
            begin
                {inner_sql};
                rdb$set_context(
                    'USER_SESSION',
                    'PACKAGED_PROC',
                    'OK'
                );
                out_result = 1;
                suspend;
            end

            function pg_func() returns int as
                {declared_ddl}
            begin
                {inner_sql};
                rdb$set_context(
                    'USER_SESSION',
                    'PACKAGED_FUNC',
                    'OK'
                );
                return 1;
            end
        end;
        commit;

        -- ###################
        -- ###  C H E C K  ###
        -- ###################
        select rdb$get_context('USER_SESSION', 'DB_LEVEL_TRG') as db_level_trg from rdb$database;
        select p.out_result as standalone_proc from sp_test p;
        select fn_test() as standalone_func from rdb$database;
        select p.out_result as packaged_proc from pg_test.pg_proc p;
        select pg_test.pg_func() as packaged_func from rdb$database;

        execute block returns(eb_result int) as
            {declared_ddl}
        begin
            {inner_sql};
            rdb$set_context(
                'USER_SESSION',
                'EXECUTE_BLOCK',
                'OK'
            );
            eb_result = 1;
            suspend;
        end;
    """
    
    tmp_sql.write_text(ddl_full, encoding = 'utf8')
    expected_stdout = f"""
        DB_LEVEL_TRG     OK
        STANDALONE_PROC  1
        STANDALONE_FUNC  1
        PACKAGED_PROC    1
        PACKAGED_FUNC    1
        EB_RESULT        1
    """
    act.expected_stdout = expected_stdout

    act.isql(switches=['-q'], charset = 'utf8', combine_output = True, input_file = tmp_sql, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
