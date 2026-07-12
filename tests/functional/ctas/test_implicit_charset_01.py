#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. Check content of RDB$ tables when record source contains literal string (extracted metadata must contain CHARACTER SET for appropriate column).
DESCRIPTION:
NOTES:
    [12.07.2026] pzotov
    Array datatypes are not checked.
    See: https://groups.google.com/g/firebird-devel/c/B78uNpDZj7s/m/36UOmjX8AQAJ
    Confirmed bug on 6.0.0.2070-d2cb23c: for literal string (see 'LET_THE_MUSIC_PLAY' column)and charset connection = utf8
    appropriate record in the RDB$FIELDS table will contain:
        RDB$FIELD_TYPE = 14
        RDB$FIELD_SUB_TYPE = 4
    Fixed by:
        https://github.com/FirebirdSQL/firebird/commit/4bf5030b255ef12090a15b85e97f78ea4b129d9b
    Checked on 6.0.0.2072-42c8a5d
"""

import pytest
from firebird.qa import *

db = db_factory(charset = 'win1252')

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_script = f"""
        set bail on;
        set blob all;
        set list on;
        set autoterm on;
        commit;

        create table test (
            f_utf8 varchar(30) character set utf8
           ,f_1254 varchar(30) character set win1254
           ,f_1252 varchar(30) -- DB-default: 1252
        );

        insert into test (
            f_utf8
           ,f_1254
           ,f_1252
        ) values(
            'Թող երաժշտությունը հնչի' -- armenian
           ,'Bırak müzik çalsın'      -- turkish
           ,'Låt musiken spela'       -- swedish
        );
        commit;

        create table ctas_test as (
            select
                t.*
               ,q'#Άσε τη μουσική να παίζει#' as let_the_music_play
            from test t
        ) with data;
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
        where rf.rdb$relation_name = coalesce( rdb$get_context('USER_SESSION','SHOW_FOR_TABLE'), upper('CTAS_TEST'))
        order by rf.rdb$field_position
        ;
        commit;

        -- this must issue: 1.
        select count(*) as uniq_rows_cnt
        from (
            select
                f_utf8
               ,f_1254
               ,f_1252
            from test
            UNION DISTINCT
            select 
                f_utf8
               ,f_1254
               ,f_1252
            from ctas_test
        )
        ;
        set count on;
        select
            rf_fld_name
            ,f_fld_type
            ,f_chr_len
            ,cset_name
            ,bytes_per_c
            ,fld_coll
            ,coll_attr
        from v_fields_info;
    """

    act.expected_stdout = """
        UNIQ_ROWS_CNT 1

        RF_FLD_NAME F_UTF8
        F_FLD_TYPE varchar
        F_CHR_LEN 30
        CSET_NAME UTF8
        BYTES_PER_C 4
        FLD_COLL UTF8
        COLL_ATTR 1
        
        RF_FLD_NAME F_1254
        F_FLD_TYPE varchar
        F_CHR_LEN 30
        CSET_NAME WIN1254
        BYTES_PER_C 1
        FLD_COLL WIN1254
        COLL_ATTR 1
        
        RF_FLD_NAME F_1252
        F_FLD_TYPE varchar
        F_CHR_LEN 30
        CSET_NAME WIN1252
        BYTES_PER_C 1
        FLD_COLL WIN1252
        COLL_ATTR 1
        
        RF_FLD_NAME LET_THE_MUSIC_PLAY
        F_FLD_TYPE char
        F_CHR_LEN 24
        CSET_NAME UTF8
        BYTES_PER_C 4
        FLD_COLL UTF8
        COLL_ATTR 1

        Records affected: 4
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True, charset = 'utf8')
    assert act.clean_stdout == act.clean_expected_stdout
