#coding:utf-8

"""
ID:          n/a
TITLE:       DECLARED TEMPORARY TABLE - basic test for datatypes.
DESCRIPTION:
    Test verifies ability to use DTT in standalone/packaged units and in triggers.
    All datatypes are checked (including non-ascii strings for textual columns).
    DTT (name = 'tbase') is created in every kind of PSQL unit and is filled with one record.
    After this, we query this record and evaluate blob_append() for all its fields ('<b>').
    Finally, CRYPT_HASH(<b> using SHA512) is applied to this result and its value is checked.
    All kind of units must operate with DTT without any error.
NOTES:
    [25.07.2026] pzotov
    Several problems have been found during this test implementation:
        https://groups.google.com/g/firebird-devel/c/M6_BAoBNRpM/m/bq6SFj3uAgAJ
        https://groups.google.com/g/firebird-devel/c/M6_BAoBNRpM/m/IVCL2oEcAwAJ
        https://groups.google.com/g/firebird-devel/c/3o-OHhJEOv0/m/0z9Zb433BgAJ
    Checked on 6.0.0.2092-92bad46.
"""
import time
import locale
from pathlib import Path
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)
tmp_sql = temp_file('test_dtt_basic.sql')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, capsys):

    declared_tt_ddl = """
        declare temporary table tbase(
            id016 smallint
           ,id032 int
           ,id064 bigint
           ,id128 int128
           ,flt float
           ,dbl double precision
           ,dec_02_2 decimal(2,2)
           ,dec_04_0 decimal(4)   -- int (exact)
           ,dec_04_2 decimal(4,2) -- int (data * 1e2)
           ,num_02_2 numeric(2,2) -- smallint
           ,num_04_0 numeric(4)   -- smallint (exact)
           ,num_04_2 numeric(4,2) -- smallint (data * 1e2)
           ,num_09_0 numeric(9)
           ,num_09_9 numeric(9,9)
           ,num_10_0 numeric(10)     -- bigint (data * 1e4)
           ,num_10_10 numeric(10,10)
           ,num_38_0 numeric(38)
           ,num_38_38 numeric(38,38) -- int128 (data * 1e6)
           ,df_16 decfloat(16)
           ,df_34 decfloat(34)
           ,dt date
           ,tm time
           ,ts timestamp
           ,tmtz time with time zone
           ,tstz timestamp with time zone
           ,tbin binary -- default length: 1
           ,tchr char(50)
           ,vbin varbinary(50)
           ,vchr_utf8 varchar(50) character set utf8
           ,vchr_1254 varchar(50) character set win1254
           ,nchr nchar(50) -- iso8859-1
           ,vnch national char varying(50)
           ,boo boolean
           ,b_bin blob sub_type 0
           ,b_txt blob sub_type 1 character set win1250 collate win_cz
        )
    """

    declared_vars_lst = """
        declare id016 smallint;
        declare id032 int;
        declare id064 bigint;
        declare id128 int128;
        declare flt float;
        declare dbl double precision;
        declare dec_02_2 decimal(2,2);
        declare dec_04_0 decimal(4);   -- int (exact)
        declare dec_04_2 decimal(4,2); -- int (data * 1e2)
        declare num_02_2 numeric(2,2); -- smallint
        declare num_04_0 numeric(4);   -- smallint (exact)
        declare num_04_2 numeric(4,2); -- smallint (data * 1e2)
        declare num_09_0 numeric(9);
        declare num_09_9 numeric(9,9);
        declare num_10_0 numeric(10);     -- bigint (data * 1e4)
        declare num_10_10 numeric(10,10);
        declare num_38_0 numeric(38);
        declare num_38_38 numeric(38,38); -- int128 (data * 1e6)
        declare df_16 decfloat(16);
        declare df_34 decfloat(34);
        declare dt date;
        declare tm time;
        declare ts timestamp;
        declare tmtz time with time zone;
        declare tstz timestamp with time zone;
        declare tbin binary; -- default length: 1;
        declare tchr char(50);
        declare vbin varbinary(50);
        declare vchr_utf8 varchar(50) character set utf8;
        declare vchr_1254 varchar(50) character set win1254;
        declare nchr nchar(50); -- iso8859-1
        declare vnch national char varying(50);
        declare boo boolean;
        declare b_bin blob sub_type 0;
        declare b_txt blob sub_type 1 character set win1250 collate win_cz;
    """

    declared_tt_dml = """
        insert into tbase(
           id016
           ,id032
           ,id064
           ,id128
           ,flt
           ,dbl
           ,dec_02_2
           ,dec_04_0
           ,dec_04_2
           ,num_02_2
           ,num_04_0
           ,num_04_2
           ,num_09_0
           ,num_09_9
           ,num_10_0
           ,num_10_10
           ,num_38_0
           ,num_38_38
           ,df_16
           ,df_34
           ,dt
           ,tm
           ,ts
           ,tmtz
           ,tstz
           ,tbin
           ,tchr
           ,vbin
           ,vchr_utf8
           ,vchr_1254
           ,nchr
           ,vnch
           ,boo
           ,b_bin
           ,b_txt
        ) values(
            -32768
           ,-2147483648
           ,-9223372036854775808
           ,-170141183460469231731687303715884105728
           ,pi()
           ,pi()
           ,-327.68
           ,-327.68
           ,-327.68
           ,-327.68
           ,-327.68
           ,-327.68
           ,999999999
           ,.999999999
           ,9999999999
           ,.9999999999
           ,99999999999999999999999999999999999999
           ,.99999999999999999999999999999999999999
           ,cast( 9.999999999999999E384 as decfloat(16))
           ,cast( 9.999999999999999999999999999999999E6144 as decfloat(34))
           ,date '01.01.0001'
           ,time '23:59:59.999'
           ,'31.12.9999 23:59:59.999'
           ,time '11:11:11.111 Indian/Cocos'
           ,timestamp '2018-12-31 12:31:42.543 Pacific/Fiji'
           ,'A'          -- binary (default len = 1)
           ,'deadbeaf'   -- tchr char(50)
           ,'deadbeaf'   -- vbin varbinary(50)
           ,'არცოდნა არცოდვააო' -- utf8
           ,q'#Son gülen iyi güler#' -- win1254
           ,q'#Tout passé, tout cassé, tout lassé#' -- iso8859-1
           ,'çèéêëìíîïð' -- national char varying(50)
           ,true
           ,x'baaaaaad0000000ff1ce'    -- blob binary
           ,q'#Bez práce nejsou koláče#' -- win1250 collate win_cz
        ) returning
           id016
           ,id032
           ,id064
           ,id128
           ,flt
           ,dbl
           ,dec_02_2
           ,dec_04_0
           ,dec_04_2
           ,num_02_2
           ,num_04_0
           ,num_04_2
           ,num_09_0
           ,num_09_9
           ,num_10_0
           ,num_10_10
           ,num_38_0
           ,num_38_38
           ,df_16
           ,df_34
           ,dt
           ,tm
           ,ts
           ,tmtz
           ,tstz
           ,tbin
           ,tchr
           ,vbin
           ,vchr_utf8
           ,vchr_1254
           ,nchr
           ,vnch
           ,boo
           ,b_bin
           ,b_txt
        into
           id016
           ,id032
           ,id064
           ,id128
           ,flt
           ,dbl
           ,dec_02_2
           ,dec_04_0
           ,dec_04_2
           ,num_02_2
           ,num_04_0
           ,num_04_2
           ,num_09_0
           ,num_09_9
           ,num_10_0
           ,num_10_10
           ,num_38_0
           ,num_38_38
           ,df_16
           ,df_34
           ,dt
           ,tm
           ,ts
           ,tmtz
           ,tstz
           ,tbin
           ,tchr
           ,vbin
           ,vchr_utf8
           ,vchr_1254
           ,nchr
           ,vnch
           ,boo
           ,b_bin
           ,b_txt
    """
    
    blob_append_hash = """
        crypt_hash (
            blob_append(
               id016
               ,id032
               ,id064
               ,id128
               ,flt
               ,dbl
               ,dec_02_2
               ,dec_04_0
               ,dec_04_2
               ,num_02_2
               ,num_04_0
               ,num_04_2
               ,num_09_0
               ,num_09_9
               ,num_10_0
               ,num_10_10
               ,num_38_0
               ,num_38_38
               ,df_16
               ,df_34
               ,dt
               ,tm
               ,ts
               ,tmtz
               ,tstz
               ,boo
               ,tbin
               ,vbin
               ,b_bin
               ,cast(tchr as blob character set none)
               ,cast(vchr_utf8 as blob character set none)
               ,cast(vchr_1254 as blob character set none)
               ,cast(nchr as blob character set none)
               ,cast(vnch as blob character set none)
               ,cast(b_txt as blob character set none)
            )
            using sha512
        )    
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
            {declared_tt_ddl};
            {declared_vars_lst}
        begin
            {declared_tt_dml};
            rdb$set_context(
                'USER_SESSION',
                'DB_LEVEL_TRG',
                {blob_append_hash}
            );
        end;

        create or alter procedure sp_test returns(
           out_result varbinary(64)
        ) as
            {declared_tt_ddl};
            {declared_vars_lst}
        begin
            {declared_tt_dml};
            out_result = {blob_append_hash};
            suspend;
        end;

        ------------------------------
        create or alter function fn_test returns varbinary(64) as
            {declared_tt_ddl};
            {declared_vars_lst}
        begin
            {declared_tt_dml};
            return {blob_append_hash};
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
                {declared_tt_dml};
                out_result = {blob_append_hash};
                suspend;
            end

            function pg_func() returns varbinary(64) as
                {declared_tt_ddl};
                {declared_vars_lst}
            begin
                {declared_tt_dml};
                return {blob_append_hash};
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
        execute block returns (execute_block_outcome varbinary(64)) as
            {declared_tt_ddl};
            {declared_vars_lst}
        begin
            {declared_tt_dml};
            execute_block_outcome = {blob_append_hash};
            suspend;
        end;
    """
    
    tmp_sql.write_text(ddl_full, encoding = 'utf8')

    COMMON_OUTCOME = '0BBA280A23C68881D3F7F71E2D96A1FD5720D2B43112CB12B2A465DA60EA40EE301E59C8141A0BFFC83ABC1DCF80E5DA7B04AFD21F5E4B84A9653D1BB946ED1E'
    expected_stdout = f"""
        DB_LEVEL_TRG                    {COMMON_OUTCOME}
        STANDALONE_PROC                 {COMMON_OUTCOME}
        STANDALONE_FUNC                 {COMMON_OUTCOME}
        PACKAGED_PROC                   {COMMON_OUTCOME}
        PACKAGED_FUNC                   {COMMON_OUTCOME}
        EXECUTE_BLOCK_OUTCOME           {COMMON_OUTCOME}
    """
    act.expected_stdout = expected_stdout

    act.isql(switches=['-q'], charset = 'utf8', combine_output = True, input_file = tmp_sql, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
