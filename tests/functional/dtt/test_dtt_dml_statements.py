#coding:utf-8

"""
ID:          n/a
TITLE:       DECLARED TEMPORARY TABLE - basic check of allowed DML statements.
DESCRIPTION:
    Test verifies ability to use DML (insert / update or insert / update / merge and delete / explicit and implicit cursors)
    against declared temporary tables in standalone/packaged units, triggers and execute blocks.
NOTES:
    [27.07.2026] pzotov
    Checked 6.0.0.2092-3fa7269.
"""
import shutil
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

    declared_tt_ddl = """
        declare temporary table tbase(
            id int
           ,fn int128
           ,bb blob sub_type 0
           ,bt blob sub_type 1 character set win1250 collate win_cz
        )
    """

    declared_vars_lst = """
        declare id int;
        declare fn int128;
        declare bb blob sub_type 0;
        declare bt blob sub_type 1 character set win1250 collate win_cz;
        declare blob_app_hash varbinary(64);
    """

    declared_tt_ins = """
        insert into tbase (
           id
           ,fn
           ,bb
           ,bt
        ) values(
            1
           ,-170141183460469231731687303715884105728
           ,x'baaaaaad0000000ff1ce'      -- blob binary
           ,q'#Bez práce nejsou koláče#' -- win1250 collate win_cz
        )
    """

    declared_tt_mer = """
        merge into tbase t
        using (
            select
                i as id
                ,-170141183460469231731687303715884105728+i as fn
                ,x'facefeed' as bb
                ,_win1250 'Každá liška svůj ocas chválí' as bt
            from generate_series(1, 2) as s(i)
        ) s
        on s.id = t.id
        when matched then
            update set t.fn = s.fn
        when NOT matched then
            insert(id, fn, bb, bt) values(s.id, s.fn, s.bb, s.bt)
    """

    declared_tt_uin = """
        update or insert into tbase  (
           id
           ,fn
           ,bb
           ,bt
        ) values(
            3
           ,170141183460469231731687303715884105727
           ,x'baadf00d'                  -- blob binary
           ,q'#Dvakrát měř, jednou řež#' -- win1250 collate win_cz
        )
        matching(id)
    """

    declared_tt_upd = """
        update tbase set
            fn = 170141183460469231731687303715884105727
            ,bb = x'facefeed'
            ,bt = 'Nedělej z komára velblouda' 
        where id = 1
    """

    declared_tt_del = """
        delete from tbase
        where bt like '%liška%'
        order by id
    """

    final_result = "crypt_hash( (select listagg(all blob_append(id, fn, bb, cast(bt as blob character set none)), ':') from tbase) using sha512 )"


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
            {declared_tt_ddl};
            {declared_vars_lst}
        begin
            {declared_tt_ins};
            {declared_tt_mer};
            {declared_tt_uin};
            {declared_tt_upd};
            {declared_tt_del};

            rdb$set_context(
                'USER_SESSION',
                'DB_LEVEL_TRG',
                {final_result}
            );
        end;

        create or alter procedure sp_test returns(
           out_result varbinary(64)
        ) as
            {declared_tt_ddl};
            {declared_vars_lst}
        begin
            {declared_tt_ins};
            {declared_tt_mer};
            {declared_tt_uin};
            {declared_tt_upd};
            {declared_tt_del};

            out_result = {final_result};
            suspend;
        end;

        ------------------------------
        create or alter function fn_test returns varbinary(64) as
            {declared_tt_ddl};
            {declared_vars_lst}
        begin
            {declared_tt_ins};
            {declared_tt_mer};
            {declared_tt_uin};
            {declared_tt_upd};
            {declared_tt_del};

            return {final_result};
        end;
        
        ------------------------------
        create or alter package pg_test as
        begin
            procedure pg_proc returns (
                out_result varbinary(64)
            );
            function pg_func() returns varbinary(64);
        end;

        recreate package body pg_test as
        begin
            procedure pg_proc returns (
               out_result varbinary(64)
            ) as
                {declared_tt_ddl};
                {declared_vars_lst}
            begin
                {declared_tt_ins};
                {declared_tt_mer};
                {declared_tt_uin};
                {declared_tt_upd};
                {declared_tt_del};

                out_result = {final_result};
                suspend;
            end

            function pg_func() returns varbinary(64) as
                {declared_tt_ddl};
                {declared_vars_lst}
            begin
                {declared_tt_ins};
                {declared_tt_mer};
                {declared_tt_uin};
                {declared_tt_upd};
                {declared_tt_del};

                return {final_result};
            end
        end;
        commit;

        -- ###################
        -- ###  C H E C K  ###
        -- ###################
        select cast(rdb$get_context('USER_SESSION', 'DB_LEVEL_TRG') as varbinary(64)) as db_level_trg from rdb$database;
        select p.out_result as standalone_proc from sp_test p;
        select fn_test() as standalone_func from rdb$database;
        select p.out_result as packaged_proc from pg_test.pg_proc p;
        select pg_test.pg_func() as packaged_func from rdb$database;
        execute block returns (eb_scalar_value varbinary(64)) as
            {declared_tt_ddl};
            {declared_vars_lst}
        begin
            {declared_tt_ins};
            {declared_tt_mer};
            {declared_tt_uin};
            {declared_tt_upd};
            {declared_tt_del};

            eb_scalar_value = {final_result};
            suspend;
        end;

        execute block returns (
            eb_implicit_cursor varbinary(64),
            eb_explicit_cursor varbinary(64)
        ) as
            {declared_tt_ddl};
            declare c cursor for (select {final_result} as val from rdb$database);
        begin
            {declared_tt_ins};
            {declared_tt_mer};
            {declared_tt_uin};
            {declared_tt_upd};
            {declared_tt_del};

            for
                select {final_result} as val
                from rdb$database
                into eb_implicit_cursor
            do begin
                open c;
                while (1=1) do
                begin
                    fetch c into eb_explicit_cursor;
                    if (row_count = 0) then leave;
                    suspend;
                end
                close c;
            end
        end;
        -- final_result

        -- this must fail with "42000 / ... / -WITH LOCK can be used only with a single physical table":
        execute block as
            {declared_tt_ddl};
        begin
            for
                select
                    id
                    ,fn
                    ,bb
                    ,bt
                from tbase
                order by id
                with lock
                as cursor c
            do begin
                -- nop --
            end
        end;
    """
    
    tmp_sql.write_text(ddl_full, encoding = 'utf8')
    shutil.copy2(tmp_sql, r'C:\FBTESTING\qa\misc\tmp.sql')

    COMMON_OUTCOME = '50986F1B51E97BEF394071812759DD597C92633C07A22997A8FFA0A7BB890B2A6FB3901407BF02CA7A11B19480400BFC40E102A6253BC14B2226035C0D0DDCF4'
    expected_stdout = f"""
        DB_LEVEL_TRG                    {COMMON_OUTCOME}
        STANDALONE_PROC                 {COMMON_OUTCOME}
        STANDALONE_FUNC                 {COMMON_OUTCOME}
        PACKAGED_PROC                   {COMMON_OUTCOME}
        PACKAGED_FUNC                   {COMMON_OUTCOME}
        EB_SCALAR_VALUE                 {COMMON_OUTCOME}
        EB_IMPLICIT_CURSOR              {COMMON_OUTCOME}
        EB_EXPLICIT_CURSOR              {COMMON_OUTCOME}

        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -WITH LOCK can be used only with a single physical table
    """
    act.expected_stdout = expected_stdout

    act.isql(switches=['-q'], charset = 'utf8', combine_output = True, input_file = tmp_sql, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
