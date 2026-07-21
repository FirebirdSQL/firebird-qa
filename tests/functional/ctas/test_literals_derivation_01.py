#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. Check content of RDB$ tables for a CTAS-table when query consists of literals.
DESCRIPTION:
NOTES:
    [21.07.2026] pzotov
    Array datatypes are not checked.
    Difference existed in the SCALE for decimal/numeric columns between original and target tables.
    Fixed in #6c797c76f (06-JUL-2026 11:22+0000).
    See: https://groups.google.com/g/firebird-devel/c/tp2UhWmljHU/m/tf-v5EHBAAAJ
    Checked on 6.0.0.2084-793c1b9
"""
import os
import pytest
from firebird.qa import *

db = db_factory(charset = 'utf8')

substitutions = [] # [('[ \t]+', ' ')]
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

        recreate table ctas_permanent as (
            select
                1 as  addi_i032
               ,-9223372036854775808 as addi_i064
               ,-170141183460469231731687303715884105728 as addi_i128
               ,pi() as addi_dbl
               ,cast( 9.999999999999999E384 as decfloat(16)) as addi_df16
               ,cast( 9.999999999999999999999999999999999E6144 as decfloat(34)) as addi_df34
               ,date '01.01.0001' as addi_dt
               ,time '23:59:59.999' as addi_tm
               ,'31.12.9999 23:59:59.999' as addi_ts
               ,time '11:11:11.111 Indian/Cocos' as addi_tmtz
               ,timestamp '2018-12-31 12:31:42.543 Pacific/Fiji' as addi_tstz
               ,rdb$db_key as addi_bin
               ,_utf8 '𒀂𒀃𒀄𒀅𒀆𒀇𒀈𒀉𒀊𒀋' as addi_utf8
               ,_win1250 'ŁŞŻŔĹĆÇČĘŮ' as addi_1250
               ,_iso8859_1 'ÁÂÃÄÅÆÇÈÉÊ' as addi_iso1
               ,true as addi_bool
               ,cast( rdb$db_key as blob sub_type binary ) as addi_bbin
               ,cast('procházky Starým Městem' as blob sub_type text character set win1250) collate win_cz as addi_btxt
               -------------------------
               ,cast(null as smallint) as null_i016
               ,cast(null as int) as null_i032
               ,cast(null as bigint) as null_i064
               ,cast(null as int128) as null_i128
               ,cast(null as float) as null_flt
               ,cast(null as double precision) as null_dbl
               ,cast(null as decimal(2,2)) as null_dec_02_2
               ,cast(null as decimal(4)) as null_dec_04_0
               ,cast(null as decimal(4,2)) as null_dec_04_2
               ,cast(null as numeric(2,2)) as null_num_02_2
               ,cast(null as numeric(4)) as null_num_04_0
               ,cast(null as numeric(4,2)) as null_num_04_2
               ,cast(null as numeric(9)) as null_num_09_0
               ,cast(null as numeric(9,9)) as null_num_09_9
               ,cast(null as numeric(10)) as null_num_10_0
               ,cast(null as numeric(10,10)) as null_num_10_10
               ,cast(null as numeric(38)) as null_num_38_0
               ,cast(null as numeric(38,38)) as null_num_28_28

               ,cast(null as decfloat(16)) as null_df16
               ,cast(null as decfloat(34)) as null_df34

               ,cast(null as date) as null_dt
               ,cast(null as time) as null_tm
               ,cast(null as timestamp) as null_ts
               ,cast(null as time with time zone) as null_tmtz
               ,cast(null as timestamp with time zone) as null_tstz
               ,cast(null as binary) as null_tbin
               ,cast(null as char) as null_tchr
               ,cast(null as varbinary(10)) as null_vbin
               ,cast(null as varchar(10) character set utf8) collate unicode_ci_ai as null_utf8
               ,cast(null as varchar(10) character set iso8859_1) collate fr_fr as null_iso1
               ,cast(null as varchar(10) character set win1250) collate win_cz_ci_ai as null_1250
               ,cast(null as boolean) as null_bool
               ,cast(null as blob sub_type binary segment size 512) as null_bbin
               ,cast(null as blob sub_type text segment size 2048 character set win1250) collate win_cz as null_btxt

            from rdb$database
        );
        execute block as begin rdb$set_context('USER_SESSION','SHOW_FOR_TABLE', 'CTAS_PERMANENT'); end;
        commit;
        set count on;
        select * from v_fields_info;
    """

    act.expected_stdout = """
        RF_FLD_NAME                     ADDI_I032
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_I064
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_I128
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_DBL
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_DF16
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_DF34
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_DT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_TM
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_TS
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      char
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       23
        CSET_NAME                       UTF8
        BYTES_PER_C                     4
        FLD_COLL                        UTF8
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     ADDI_TMTZ
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_TSTZ
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_BIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      char
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       8
        CSET_NAME                       OCTETS
        BYTES_PER_C                     1
        FLD_COLL                        OCTETS
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     ADDI_UTF8
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_1250
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      char
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       20
        CSET_NAME                       WIN1250
        BYTES_PER_C                     1
        FLD_COLL                        WIN1250
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     ADDI_ISO1
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      char
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       20
        CSET_NAME                       ISO8859_1
        BYTES_PER_C                     1
        FLD_COLL                        ISO8859_1
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     ADDI_BOOL
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_BBIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     ADDI_BTXT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     1
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_I016
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_I032
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_I064
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_I128
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_FLT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_DBL
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_DEC_02_2
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      9
        F_FLD_SCALE                     -2
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NULL_DEC_04_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_DEC_04_2
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      decimal
        F_FLD_PREC                      9
        F_FLD_SCALE                     -2
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NULL_NUM_02_2
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      4
        F_FLD_SCALE                     -2
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NULL_NUM_04_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_NUM_04_2
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      4
        F_FLD_SCALE                     -2
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NULL_NUM_09_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_NUM_09_9
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_NUM_10_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_NUM_10_10
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      numeric
        F_FLD_PREC                      18
        F_FLD_SCALE                     -10
        F_CHR_LEN                       <null>
        CSET_NAME                       <null>
        BYTES_PER_C                     <null>
        FLD_COLL                        <null>
        COLL_ATTR                       <null>
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NULL_NUM_38_0
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_NUM_28_28
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_DF16
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_DF34
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_DT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_TM
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_TS
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_TMTZ
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_TSTZ
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_TBIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      char
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       1
        CSET_NAME                       OCTETS
        BYTES_PER_C                     1
        FLD_COLL                        OCTETS
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NULL_TCHR
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      char
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       1
        CSET_NAME                       UTF8
        BYTES_PER_C                     4
        FLD_COLL                        UTF8
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NULL_VBIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
        F_FLD_TYPE                      varchar
        F_FLD_PREC                      <null>
        F_FLD_SCALE                     0
        F_CHR_LEN                       10
        CSET_NAME                       OCTETS
        BYTES_PER_C                     1
        FLD_COLL                        OCTETS
        COLL_ATTR                       1
        RF_IS_EXPR                      0
        F_FLD_EXPR_BLOB_ID              <null>
        RF_FLD_NAME                     NULL_UTF8
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_ISO1
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_1250
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_BOOL
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_BBIN
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        RF_FLD_NAME                     NULL_BTXT
        RF_FLD_SOURCE                   RDB_NNNN
        RF_NOT_NULL                     <null>
        RF_DEFAULT                      <null>
        RF_IDENT_TYPE                   <null>
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
        Records affected: 52
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True, charset = 'utf8')
    assert act.clean_stdout == act.clean_expected_stdout
