#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. Check content of RDB$ tables for a CTAS-table when field types are specified directly in the table DDL (i.e. not via domains).
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
        set width rf_fld_name 20;
        set width rf_fld_source 20;
        set width f_fld_type 50;
        set width cset_name 20;
        set width fld_coll 20;
        set width coll_attr 30;
        
        set list on;
        set autoterm on;
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
            
            -- no need ed for this test:
            --,rf.rdb$default_source as rf_default
            --,rf.rdb$identity_type as rf_ident_type

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
        
        recreate table tbase(
            id016 smallint
           ,id032 int
           ,id064 bigint
           ,id128 int128
           ,flt float
           ,dbl double precision

           ,dec_01_0  decimal(1)    -- int
           ,dec_04_0  decimal(4)    -- int
           ,dec_05_0  decimal(5)    -- int
           ,dec_09_0  decimal(9)    -- int
           ,dec_18_0  decimal(18)   -- bigint
           ,dec_38_0  decimal(38)   -- int128

           ,dec_01_1  decimal(1, 1)  -- int
           ,dec_04_4  decimal(4, 4)  -- int
           ,dec_05_5  decimal(5, 5)  -- int
           ,dec_09_9  decimal(9, 9)  -- int
           ,dec_18_18 decimal(18,18) -- bigint
           ,dec_38_38 decimal(38,38) -- int128

           ,num_01_0 numeric(1)    -- smallint
           ,num_04_0 numeric(4)    -- smallint
           ,num_05_0 numeric(5)    -- int
           ,num_09_0 numeric(9)    -- int
           ,num_18_0 numeric(18)   -- bigint
           ,num_38_0 numeric(38)   -- int128

           ,num_01_1  numeric(1, 1)  -- smallint
           ,num_04_4  numeric(4, 4)  -- smallint
           ,num_05_5  numeric(5, 5)  -- int
           ,num_09_9  numeric(9, 9)  -- int
           ,num_18_18 numeric(18,18) -- bigint
           ,num_38_38 numeric(38,38) -- int128

           ,df_16 decfloat(16)
           ,df_34 decfloat(34)

           ,dt date
           ,tm time
           ,ts timestamp
           ,tmtz time with time zone
           ,tstz timestamp with time zone
           ,tbin binary -- default length: 1
           ,tchr char(10)
           ,vbin varbinary(10)

           ,vchr_utf8 varchar(10) character set utf8 collate unicode_ci_ai
           ,vchr_iso1 varchar(10) character set iso8859_1 collate fr_fr
           ,vchr_1250 varchar(10) character set win1250 collate win_cz_ci_ai
           ,boo boolean

           ,bbin blob sub_type binary segment size 512
           ,btxt blob sub_type text segment size 2048 character set win1250 collate win_cz


           -- ##########################################
           -- ###   c o m p u t e d     f i e l d s  ###
           -- ##########################################
           ,comp_id016 computed by ( id016 - 1 )
           ,comp_id032 computed by ( id032 - 1 )
           ,comp_id064 computed by ( id064 - 1 )
           ,comp_id128 computed by ( id128 - 1 )

           ,comp_flt computed by (flt + 0e0)
           ,comp_dbl computed by (dbl + 0e0)

           ,comp_dec_01_0 computed by( dec_01_0 + 0 )
           ,comp_dec_04_0 computed by( dec_04_0 + 0 )
           ,comp_dec_05_0 computed by( dec_05_0 + 0 )
           ,comp_dec_09_0 computed by( dec_09_0 + 0 )
           ,comp_dec_18_0 computed by( dec_18_0 + 0 )
           ,comp_dec_38_0 computed by( dec_38_0 + 0 )

           ,comp_dec_01_1 computed by( dec_01_1 + 0 )
           ,comp_dec_04_4 computed by( dec_04_4 + 0 )
           ,comp_dec_05_5 computed by( dec_05_5 + 0 )
           ,comp_dec_09_9 computed by( dec_09_9 + 0 )
           ,comp_dec_18_18 computed by( dec_18_18 + 0 )
           ,comp_dec_38_18 computed by( dec_38_38 + 0 )

           ,comp_num_01_0 computed by( num_01_0 + 0 )
           ,comp_num_04_0 computed by( num_04_0 + 0 )
           ,comp_num_05_0 computed by( num_05_0 + 0 )
           ,comp_num_09_0 computed by( num_09_0 + 0 )
           ,comp_num_18_0 computed by( num_18_0 + 0 )
           ,comp_num_38_0 computed by( num_38_0 + 0 )

           ,comp_num_01_1 computed by( num_01_1 + 0 )
           ,comp_num_04_4 computed by( num_04_4 + 0 )
           ,comp_num_05_5 computed by( num_05_5 + 0 )
           ,comp_num_09_9 computed by( num_09_9 + 0 )
           ,comp_num_18_18 computed by( num_18_18 + 0 )
           ,comp_num_38_18 computed by( num_38_38 + 0 )

           ,comp_dt computed by ( dt + 1 )
           ,comp_tm computed by ( dateadd(1 second to tm) )
           ,comp_ts computed by ( ts - 1 )

           ,comp_tmtz computed by ( dateadd(1 second to tmtz) )
           ,comp_tstz computed by ( tstz - 1 )

           ,comp_vchr_utf8 computed by ( reverse(vchr_utf8) )
           ,comp_vchr_1250 computed by ( lower(vchr_1250) )
           ,comp_boo computed by ( not boo )
           ,comp_bbin computed by ( bbin )
           ,comp_btxt computed by ( reverse(btxt) )
        );
        recreate table ctas_permanent as (select * from tbase);
        execute block as begin rdb$set_context('USER_SESSION','SHOW_FOR_TABLE', 'CTAS_PERMANENT'); end;
        commit;
        set count on;
        select * from v_fields_info;
    """

    act.expected_stdout = """
        RF_FLD_NAME                     ID016
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      smallint
        F_FLD_PREC                      0
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     ID032
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      integer
        F_FLD_PREC                      0
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     ID064
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      bigint
        F_FLD_PREC                      0
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     ID128
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      int128
        F_FLD_PREC                      0
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     FLT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      float
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DBL
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      double precision
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_01_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      1
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_04_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      4
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_05_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      5
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_09_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      9
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_18_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_38_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      38
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_01_1
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      1
        F_FLD_SCALE                     -1
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_04_4
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      4
        F_FLD_SCALE                     -4
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_05_5
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      5
        F_FLD_SCALE                     -5
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_09_9
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      9
        F_FLD_SCALE                     -9
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_18_18
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     -18
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DEC_38_38
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      38
        F_FLD_SCALE                     -38
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_01_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      1
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_04_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      4
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_05_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      5
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_09_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      9
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_18_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_38_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      38
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_01_1
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      1
        F_FLD_SCALE                     -1
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_04_4
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      4
        F_FLD_SCALE                     -4
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_05_5
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      5
        F_FLD_SCALE                     -5
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_09_9
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      9
        F_FLD_SCALE                     -9
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_18_18
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     -18
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NUM_38_38
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      38
        F_FLD_SCALE                     -38
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DF_16
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decfloat(16)
        F_FLD_PREC                      16
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DF_34
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decfloat(34)
        F_FLD_PREC                      34
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     DT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      date
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     TM
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      time without time zone
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     TS
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      timestamp without time zone
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     TMTZ
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      time with time zone
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     TSTZ
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      timestamp with time zone
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     TBIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      binary
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       1
        CSET_NAME                       OCTETS
        BYTES_PER_C                     1
        FLD_COLL                        OCTETS
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     TCHR
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      char
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       10
        CSET_NAME                       UTF8
        BYTES_PER_C                     4
        FLD_COLL                        UTF8
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     VBIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      varbinary
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       10
        CSET_NAME                       OCTETS
        BYTES_PER_C                     1
        FLD_COLL                        OCTETS
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     VCHR_UTF8
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      varchar
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       10
        CSET_NAME                       UTF8
        BYTES_PER_C                     4
        FLD_COLL                        UNICODE_CI_AI
        COLL_ATTR                       7
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     VCHR_ISO1
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      varchar
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       10
        CSET_NAME                       ISO8859_1
        BYTES_PER_C                     1
        FLD_COLL                        FR_FR
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     VCHR_1250
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      varchar
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       10
        CSET_NAME                       WIN1250
        BYTES_PER_C                     1
        FLD_COLL                        WIN_CZ_CI_AI
        COLL_ATTR                       7
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     BOO
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      boolean
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     BBIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      blob sub_type binary segment size 512
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     BTXT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      blob sub_type text segment size 2048
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       WIN1250
        BYTES_PER_C                     1
        FLD_COLL                        WIN_CZ
        COLL_ATTR                       3
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_ID016
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      bigint
        F_FLD_PREC                      0
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_ID032
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      bigint
        F_FLD_PREC                      0
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_ID064
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      bigint
        F_FLD_PREC                      0
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_ID128
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      int128
        F_FLD_PREC                      0
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_FLT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      double precision
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DBL
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      double precision
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_01_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_04_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_05_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_09_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_18_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_38_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      38
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_01_1
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     -1
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_04_4
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     -4
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_05_5
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     -5
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_09_9
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     -9
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_18_18
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      18
        F_FLD_SCALE                     -18
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DEC_38_18
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      38
        F_FLD_SCALE                     -38
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_01_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_04_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_05_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_09_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_18_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_38_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      38
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_01_1
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     -1
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_04_4
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     -4
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_05_5
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     -5
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_09_9
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     -9
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_18_18
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     -18
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_NUM_38_18
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      38
        F_FLD_SCALE                     -38
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_DT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      date
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_TM
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      time without time zone
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_TS
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      timestamp without time zone
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_TMTZ
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      time with time zone
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_TSTZ
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      timestamp with time zone
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_VCHR_UTF8
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      varchar
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       10
        CSET_NAME                       UTF8
        BYTES_PER_C                     4
        FLD_COLL                        UNICODE_CI_AI
        COLL_ATTR                       7
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_VCHR_1250
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      varchar
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       10
        CSET_NAME                       WIN1250
        BYTES_PER_C                     1
        FLD_COLL                        WIN_CZ_CI_AI
        COLL_ATTR                       7
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_BOO
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      boolean
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_BBIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      blob sub_type binary segment size 80
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     COMP_BTXT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        F_FLD_TYPE                      blob sub_type text segment size 80
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       <null>
        CSET_NAME                       WIN1250
        BYTES_PER_C                     1
        FLD_COLL                        WIN_CZ
        COLL_ATTR                       3
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        Records affected: 86
    """
    act.isql(switches = ['-q', '-pag', '999999'], input = test_script, combine_output = True, charset = 'utf8')
    assert act.clean_stdout == act.clean_expected_stdout
