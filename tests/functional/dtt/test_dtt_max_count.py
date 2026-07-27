#coding:utf-8

"""
ID:          n/a
TITLE:       DECLARED TEMPORARY TABLE - check max limit for DTT that can be created within each kind of PSQL unit.
DESCRIPTION:
    Test verifies ability to create up to 1024 DTT in PSQL utins (standalone/packaged proc and func; triggers).
    An attempt to create more DTTs must fail.
NOTES:
    [27.07.2026] pzotov
    1. Test time is about 180". Probably this test checks must be reduced only to procedure and trigger.
    2. Despite that we *can* create 1024 DTTs, there is no ability to use all of them. An attempt to do that will
       fail with "Too many concurrent executions of the same request" (maxn 256 allowed).
       Because of that, test verifies *only* ability to declare sum number of DTTs, without further handling them.
    Checked 6.0.0.2092-3fa7269.
"""
#import shutil
import locale
from pathlib import Path
import pytest
from firebird.qa import *

db = db_factory()

################
MAX_COUNT = 1024
################

substitutions = [('[ \t]+', ' '), ('After line \\d+.*', '')]
act = python_act('db', substitutions = substitutions)
tmp_sql = temp_file('test_dtt_dml_statements.sql')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, capsys):

    declared_tt_ddl = '\n'.join( [ 'declare temporary table tbase_%d(id int);' % i for i in range(MAX_COUNT) ] )
    declared_tt_dml = '\n'.join( [ "insert into tbase_%d(id) values(%d);" % (i,i) for i in range(MAX_COUNT) ] )
    eval_id_total = '\n'.join( [ 'v_total = v_total + (select id from tbase_%d rows 1);' % i for i in range(MAX_COUNT) ] )

    ddl_full = f"""
        set bail on;
        set blob all;
        set list on;
        set autoterm on;
        set autoddl off;
        commit;

        create or alter procedure sp_test returns(out_result int) as
            {declared_tt_ddl}
        begin
            out_result = 1;
            suspend;
        end;
        ------------------------------
        create or alter function fn_test returns int as
            {declared_tt_ddl}
        begin
            return 1;
        end;
        ------------------------------
        create or alter package pg_test as
        begin
            procedure pg_proc returns (out_result int);
            function pg_func() returns int;
        end;

        recreate package body pg_test as
        begin
            procedure pg_proc returns (out_result int) as
                {declared_tt_ddl}
            begin
                out_result = 1;
                suspend;
            end

            function pg_func() returns int as
                {declared_tt_ddl}
            begin
                return 1;
            end
        end;
        ------------------------------
        create or alter trigger trg_tx_commit on transaction commit as
            {declared_tt_ddl}
        begin
            rdb$set_context('USER_SESSION', 'DB_LEVEL_TRG', 1);
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

        create or alter trigger trg_tx_commit on transaction commit as
            {declared_tt_ddl}
            declare temporary table t_addi(id int);
        begin
            rdb$set_context('USER_SESSION', 'DB_LEVEL_TRG', 1);
        end;

        -- this must fail with "54000 / Implementation limit exceeded / -Too many local temporary tables declared in a single statement":
        commit;
    """
    
    tmp_sql.write_text(ddl_full, encoding = 'utf8')
    #shutil.copy2(tmp_sql, r'C:\FBTESTING\qa\misc\tmp.sql')

    expected_stdout = f"""
        DB_LEVEL_TRG    1
        STANDALONE_PROC 1
        STANDALONE_FUNC 1
        PACKAGED_PROC 1
        PACKAGED_FUNC 1

        Statement failed, SQLSTATE = 54000
        Implementation limit exceeded
        -Too many local temporary tables declared in a single statement
    """
    act.expected_stdout = expected_stdout

    act.isql(switches=['-q'], charset = 'utf8', combine_output = True, input_file = tmp_sql, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
