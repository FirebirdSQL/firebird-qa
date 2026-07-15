#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. Check content of RDB$ tables for a CTAS-table when field types are specified via DOMAINS.
DESCRIPTION:
NOTES:
    [11.07.2026] pzotov
        Array datatypes are not checked.
        Difference existed in the SCALE for decimal/numeric columns between original and target tables.
        Fixed in #6c797c76f (06-JUL-2026 11:22+0000).
        See: https://groups.google.com/g/firebird-devel/c/tp2UhWmljHU/m/tf-v5EHBAAAJ
        Checked on 6.0.0.2072-42c8a5d
    [15.07.2026] pzotov
        Adjusted expected output to actual one that become since #7df850dd ("Fix some field precision of CTAS").
        Problem was for COMPUTED-BY columns defined in the source table on basis of INTEGER fields (id016, id032, id064 and id128).
        For these columns table RDB$FIELDS contained incorrect non-zero values in the RDB$FIELD_PRECICION (all must be zero).
        NOTE. To make comparison between 'old' and 'new' outputs easier, one may to change following in the script:
            * comment out 'set list on;'
            * temporary set substitutions = []
            * temporary set act.expected_stdout = ''.
        Confirmed wrong values of RDB$FIELDS.RDB$FIELD_PRECICION for integer-based columns on 6.0.0.2073-3518df8.
        Checked on 6.0.0.2074-7df850d.
"""
import os
import pytest
from firebird.qa import *

db = db_factory(charset = 'utf8')

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    null_dev = os.devnull

    test_script = f"""
        set bail on;
        set blob all;
        set list on;
        set autoterm on;
        set autoddl off;
        commit;

        create or alter function fn_get_type_name(a_type smallint, a_subtype smallint, a_blob_segment_len int = 0) returns varchar(2048) as
            declare ftype varchar(2048);
            declare segm_suffix varchar(50) = '';
        begin
            if (a_blob_segment_len > 0) then
                segm_suffix = ' segment size ' || a_blob_segment_len;

            ftype = 
                decode( a_type
                        ,  7, decode(coalesce(a_subtype,0),  0, 'smallint',             1, 'numeric', 'unknown') -- 1 => small numerics [-327.68..327.67] (i.e. with mantissa that can be fit in -32768 ... 32767)
                        ,  8, decode(coalesce(a_subtype,0),  0, 'integer',              1, 'numeric', 2, 'decimal', 'unknown') -- 1: for numeric with mantissa >= 32768 and up to 9 digits, 2: for decimals up to 9 digits
                        , 10, 'float'
                        , 12, 'date'
                        , 13, 'time without time zone'
                        , 14, decode(coalesce(a_subtype,0),  0, 'char',                 1, 'binary', 'unknown')
                        , 16, decode(coalesce(a_subtype,0),  0, 'bigint',               1, 'numeric', 2, 'decimal', 'unknown')
                        , 23, 'boolean'
                        , 24, 'decfloat(16)'
                        , 25, 'decfloat(34)'
                        , 26, decode(coalesce(a_subtype,0),  0, 'int128',              1, 'numeric', 2, 'decimal', 'unknown')
                        , 27, 'double precision' -- also for numeric and decimal, both with size >= 10, if sql_dialect = 1
                        , 28, 'time with time zone'
                        , 29, 'timestamp with time zone'
                        , 35, 'timestamp without time zone'
                        , 37, decode(coalesce(a_subtype,0),  0, 'varchar',              1, 'varbinary', 'unknown')
                        ,261, decode(coalesce(a_subtype,0),  0, 'blob sub_type binary' || segm_suffix, 1, 'blob sub_type text' || segm_suffix, 'unknown')
                      );
            if (ftype = 'unknown') then
                ftype = ftype || '__type_'  || coalesce(a_type, '[null]') || '__subtype_' || coalesce(a_subtype, '[null]');
            return ftype;
        end
        ;

        create view v_fields_info as
        select
            rf.rdb$field_name as rf_fld_name
            ,iif( trim(trailing from rf.rdb$field_source) similar to 'RDB$[[:DIGIT:]]+', 'RDB_NNNN', rf.rdb$field_source) as rf_fld_source
            ,rf.rdb$null_flag as rf_not_null
            ,rf.rdb$default_source as rf_default
            ,rf.rdb$identity_type as rf_ident_type
            ,lower(fn_get_type_name(f.rdb$field_type, f.rdb$field_sub_type, f.rdb$segment_length)) as f_fld_type
            ,f.rdb$field_precision as f_fld_prec
            ,f.rdb$field_scale as f_fld_scale
            ,f.rdb$character_length as f_chr_len
            ,c.rdb$character_set_name as cset_name
            ,c.rdb$bytes_per_character as bytes_per_c
            ,k.rdb$collation_name as fld_coll
            ,k.rdb$collation_attributes as coll_attr
            ,1-coalesce(rf.rdb$update_flag, 0) as rf_is_expr
            ,f.rdb$computed_source as f_fld_expr_blob_id
        from rdb$relation_fields rf
        join rdb$fields f on rf.rdb$field_source = f.rdb$field_name
        left join rdb$character_sets c on f.rdb$character_set_id = c.rdb$character_set_id
        left join rdb$collations k on c.rdb$character_set_id = k.rdb$character_set_id and f.rdb$collation_id = k.rdb$collation_id
        where rf.rdb$relation_name = coalesce( rdb$get_context('USER_SESSION','SHOW_FOR_TABLE'), upper('TEST'))
        order by rf.rdb$field_position
        ;

        /*
        https://www.firebirdsql.org/file/documentation/html/en/refdocs/fblangref50/firebird-50-language-reference.html#fblangref50-datatypes
        Precision   Data type            Dialect 3
         1 ...  4   NUMERIC              SMALLINT
         1 ...  4   DECIMAL              INTEGER
         5 ...  9   NUMERIC or DECIMAL   INTEGER
        10 ... 18   NUMERIC or DECIMAL   BIGINT
        19 ... 38   NUMERIC or DECIMAL   INT128
        */

        create domain id016 smallint;
        create domain id032 int;
        create domain id064 bigint;
        create domain id128 int128;
        create domain flt float;
        create domain dbl double precision;

        create domain dec_01_0  decimal(1);    -- int
        create domain dec_04_0  decimal(4);    -- int
        create domain dec_05_0  decimal(5);    -- int
        create domain dec_09_0  decimal(9);    -- int
        create domain dec_18_0  decimal(18);   -- bigint
        create domain dec_38_0  decimal(38);   -- int128

        create domain dec_01_1  decimal(1, 1);  -- int
        create domain dec_04_4  decimal(4, 4);  -- int
        create domain dec_05_5  decimal(5, 5);  -- int
        create domain dec_09_9  decimal(9, 9);  -- int
        create domain dec_18_18 decimal(18,18); -- bigint
        create domain dec_38_38 decimal(38,38); -- int128

        create domain num_01_0 numeric(1);    -- smallint
        create domain num_04_0 numeric(4);    -- smallint
        create domain num_05_0 numeric(5);    -- int
        create domain num_09_0 numeric(9);    -- int
        create domain num_18_0 numeric(18);   -- bigint
        create domain num_38_0 numeric(38);   -- int128

        create domain num_01_1  numeric(1, 1);  -- smallint
        create domain num_04_4  numeric(4, 4);  -- smallint
        create domain num_05_5  numeric(5, 5);  -- int
        create domain num_09_9  numeric(9, 9);  -- int
        create domain num_18_18 numeric(18,18); -- bigint
        create domain num_38_38 numeric(38,38); -- int128

        create domain df_16 decfloat(16);
        create domain df_34 decfloat(34);
        create domain dt date;
        create domain tm time;
        create domain ts timestamp;
        create domain tmtz time with time zone;
        create domain tstz timestamp with time zone;
        create domain tbin binary; -- default length: 1;
        create domain tchr char(10);
        create domain vbin varbinary(10);
        create domain vchr_utf8 varchar(10) character set utf8 collate unicode_ci_ai;
        create domain vchr_iso1 varchar(10) character set iso8859_1 collate fr_fr;
        create domain vchr_1250 varchar(10) character set win1250 collate win_cz_ci_ai;
        create domain boo boolean;
        create domain bbin blob sub_type binary segment size 512;
        create domain btxt blob sub_type text segment size 2048 character set win1250 collate win_cz;
        commit;

        recreate table tbase(
            id016       id016
           ,id032       id032
           ,id064       id064
           ,id128       id128
           ,flt         flt
           ,dbl         dbl

           ,dec_01_0    dec_01_0
           ,dec_04_0    dec_04_0
           ,dec_05_0    dec_05_0
           ,dec_09_0    dec_09_0
           ,dec_18_0    dec_18_0
           ,dec_38_0    dec_38_0
                       
           ,dec_01_1    dec_01_1
           ,dec_04_4    dec_04_4
           ,dec_05_5    dec_05_5
           ,dec_09_9    dec_09_9
           ,dec_18_18   dec_18_18
           ,dec_38_38   dec_38_38
                       
           ,num_01_0    num_01_0
           ,num_04_0    num_04_0
           ,num_05_0    num_05_0
           ,num_09_0    num_09_0
           ,num_18_0    num_18_0
           ,num_38_0    num_38_0
                       
           ,num_01_1    num_01_1
           ,num_04_4    num_04_4
           ,num_05_5    num_05_5
           ,num_09_9    num_09_9
           ,num_18_18   num_18_18
           ,num_38_38   num_38_38

           ,df_16       df_16
           ,df_34       df_34
           ,dt          dt
           ,tm          tm
           ,ts          ts
           ,tmtz        tmtz
           ,tstz        tstz
           ,tbin        tbin
           ,tchr        tchr
           ,vbin        vbin
           ,vchr_utf8   vchr_utf8
           ,vchr_iso1   vchr_iso1
           ,vchr_1250   vchr_1250
           ,boo         boo
           ,bbin        bbin
           ,btxt        btxt
        );
        recreate table ctas_permanent as (select * from tbase);
        execute block as begin rdb$set_context('USER_SESSION','SHOW_FOR_TABLE', 'CTAS_PERMANENT'); end;
        commit;
        set count on;
        select * from v_fields_info;
    """

    act.expected_stdout = """
        RF_FLD_NAME ID016
        RF_FLD_SOURCE ID016
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE smallint
        F_FLD_PREC 0
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME ID032
        RF_FLD_SOURCE ID032
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE integer
        F_FLD_PREC 0
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME ID064
        RF_FLD_SOURCE ID064
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE bigint
        F_FLD_PREC 0
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME ID128
        RF_FLD_SOURCE ID128
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE int128
        F_FLD_PREC 0
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME FLT
        RF_FLD_SOURCE FLT
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE float
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DBL
        RF_FLD_SOURCE DBL
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE double precision
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_01_0
        RF_FLD_SOURCE DEC_01_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 1
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_04_0
        RF_FLD_SOURCE DEC_04_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 4
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_05_0
        RF_FLD_SOURCE DEC_05_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 5
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_09_0
        RF_FLD_SOURCE DEC_09_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 9
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_18_0
        RF_FLD_SOURCE DEC_18_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 18
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_38_0
        RF_FLD_SOURCE DEC_38_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 38
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_01_1
        RF_FLD_SOURCE DEC_01_1
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 1
        F_FLD_SCALE -1
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_04_4
        RF_FLD_SOURCE DEC_04_4
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 4
        F_FLD_SCALE -4
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_05_5
        RF_FLD_SOURCE DEC_05_5
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 5
        F_FLD_SCALE -5
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_09_9
        RF_FLD_SOURCE DEC_09_9
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 9
        F_FLD_SCALE -9
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_18_18
        RF_FLD_SOURCE DEC_18_18
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 18
        F_FLD_SCALE -18
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DEC_38_38
        RF_FLD_SOURCE DEC_38_38
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 38
        F_FLD_SCALE -38
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_01_0
        RF_FLD_SOURCE NUM_01_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 1
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_04_0
        RF_FLD_SOURCE NUM_04_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 4
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_05_0
        RF_FLD_SOURCE NUM_05_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 5
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_09_0
        RF_FLD_SOURCE NUM_09_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 9
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_18_0
        RF_FLD_SOURCE NUM_18_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 18
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_38_0
        RF_FLD_SOURCE NUM_38_0
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 38
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_01_1
        RF_FLD_SOURCE NUM_01_1
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 1
        F_FLD_SCALE -1
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_04_4
        RF_FLD_SOURCE NUM_04_4
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 4
        F_FLD_SCALE -4
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_05_5
        RF_FLD_SOURCE NUM_05_5
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 5
        F_FLD_SCALE -5
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_09_9
        RF_FLD_SOURCE NUM_09_9
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 9
        F_FLD_SCALE -9
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_18_18
        RF_FLD_SOURCE NUM_18_18
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 18
        F_FLD_SCALE -18
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME NUM_38_38
        RF_FLD_SOURCE NUM_38_38
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 38
        F_FLD_SCALE -38
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DF_16
        RF_FLD_SOURCE DF_16
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decfloat(16)
        F_FLD_PREC 16
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DF_34
        RF_FLD_SOURCE DF_34
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE decfloat(34)
        F_FLD_PREC 34
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME DT
        RF_FLD_SOURCE DT
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE date
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME TM
        RF_FLD_SOURCE TM
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE time without time zone
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME TS
        RF_FLD_SOURCE TS
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE timestamp without time zone
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME TMTZ
        RF_FLD_SOURCE TMTZ
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE time with time zone
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME TSTZ
        RF_FLD_SOURCE TSTZ
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE timestamp with time zone
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME TBIN
        RF_FLD_SOURCE TBIN
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE binary
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 1
        CSET_NAME OCTETS
        BYTES_PER_C 1
        FLD_COLL OCTETS
        COLL_ATTR 1
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME TCHR
        RF_FLD_SOURCE TCHR
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE char
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 10
        CSET_NAME UTF8
        BYTES_PER_C 4
        FLD_COLL UTF8
        COLL_ATTR 1
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME VBIN
        RF_FLD_SOURCE VBIN
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE varbinary
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 10
        CSET_NAME OCTETS
        BYTES_PER_C 1
        FLD_COLL OCTETS
        COLL_ATTR 1
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME VCHR_UTF8
        RF_FLD_SOURCE VCHR_UTF8
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE varchar
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 10
        CSET_NAME UTF8
        BYTES_PER_C 4
        FLD_COLL UNICODE_CI_AI
        COLL_ATTR 7
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME VCHR_ISO1
        RF_FLD_SOURCE VCHR_ISO1
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE varchar
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 10
        CSET_NAME ISO8859_1
        BYTES_PER_C 1
        FLD_COLL FR_FR
        COLL_ATTR 1
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME VCHR_1250
        RF_FLD_SOURCE VCHR_1250
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE varchar
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 10
        CSET_NAME WIN1250
        BYTES_PER_C 1
        FLD_COLL WIN_CZ_CI_AI
        COLL_ATTR 7
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME BOO
        RF_FLD_SOURCE BOO
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE boolean
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME BBIN
        RF_FLD_SOURCE BBIN
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE blob sub_type binary segment size 512
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        RF_FLD_NAME BTXT
        RF_FLD_SOURCE BTXT
        RF_NOT_NULL <null>
        RF_DEFAULT <null>
        RF_IDENT_TYPE <null>
        F_FLD_TYPE blob sub_type text segment size 2048
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME WIN1250
        BYTES_PER_C 1
        FLD_COLL WIN_CZ
        COLL_ATTR 3
        RF_IS_EXPR 0
        F_FLD_EXPR_BLOB_ID <null>
        Records affected: 46
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True, charset = 'utf8')
    assert act.clean_stdout == act.clean_expected_stdout
