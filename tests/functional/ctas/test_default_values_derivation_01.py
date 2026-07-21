#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. DEFAULT value for a column must be derived only from DOMAIN. Dedicated default from FIELD definition must not present in the target table.
DESCRIPTION:
NOTES:
    [21.07.2026] pzotov
    Checked on 6.0.0.2084-793c1b9.
"""

import pytest
from firebird.qa import *

db = db_factory(charset = 'utf8')

substitutions = [(r'.*_BLOB_ID\s+\d+.*', ''), ('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_script = f"""
        set bail on;
        set blob all;
        set list on;
        set autoterm on;
        set autoddl off;
        commit;

        set term ^;
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
        ^ 
        set term ;^

        create view v_fields_info as
        select
            rf.rdb$field_name as rf_fld_name
            ,iif( trim(trailing from rf.rdb$field_source) similar to 'RDB$[[:DIGIT:]]+', 'RDB_NNNN', rf.rdb$field_source) as rf_fld_source
            ,rf.rdb$null_flag as rf_not_null
            ,lower(fn_get_type_name(f.rdb$field_type, f.rdb$field_sub_type, f.rdb$segment_length)) as f_fld_type
            ,f.rdb$field_precision as f_fld_prec
            ,f.rdb$field_scale as f_fld_scale
            ,f.rdb$character_length as f_chr_len
            ,c.rdb$character_set_name as cset_name
            ,c.rdb$bytes_per_character as bytes_per_c
            ,k.rdb$collation_name as fld_coll
            ,k.rdb$collation_attributes as coll_attr
            ,rf.rdb$default_source as rf_default_blob_id
            ,f.rdb$default_source as f_default_blob_id
        from rdb$relation_fields rf
        join rdb$fields f on rf.rdb$field_source = f.rdb$field_name
        left join rdb$character_sets c on f.rdb$character_set_id = c.rdb$character_set_id
        left join rdb$collations k on c.rdb$character_set_id = k.rdb$character_set_id and f.rdb$collation_id = k.rdb$collation_id
        where rf.rdb$relation_name = coalesce( rdb$get_context('USER_SESSION','SHOW_FOR_TABLE'), upper('TEST'))
        order by rf.rdb$field_position
        ;
        commit;

        /*
        https://www.firebirdsql.org/file/documentation/html/en/refdocs/fblangref50/firebird-50-language-reference.html#fblangref50-datatypes
        Precision   Data type            Dialect 3
         1 ...  4   NUMERIC              SMALLINT
         1 ...  4   DECIMAL              INTEGER
         5 ...  9   NUMERIC or DECIMAL   INTEGER
        10 ... 18   NUMERIC or DECIMAL   BIGINT
        19 ... 38   NUMERIC or DECIMAL   INT128
        */

        create domain id016 smallint default -32768;
        create domain id032 int default -2147483648;
        create domain id064 bigint default -9223372036854775808;
        create domain id128 int128 default -170141183460469231731687303715884105728;
        create domain flt float default -1e1;
        create domain dbl double precision default -1e1;

        create domain dec_05_0 decimal(5,0) default -327.68;
        create domain dec_18_0 decimal(18) default -987654321098765432;
        create domain dec_38_0 decimal(38) default -98765432109876543210987654321098765432;

        create domain num_05_0 numeric(5,0) default -327.68;
        create domain num_18_0 numeric(18) default -987654321098765432;
        create domain num_38_0 numeric(38) default -98765432109876543210987654321098765432;

        create domain df_16 decfloat(16) default -9.999999999999999E384;
        create domain df_34 decfloat(34) default -9.999999999999999999999999999999999E6144;
        create domain dt date default '01.02.2003';
        create domain tm time default '01:02:03.456';
        create domain ts timestamp default '01.02.2003 01:02:03.456';
        create domain tmtz time with time zone default '01:02:03.456 Indian/Cocos';
        create domain tstz timestamp with time zone default '01.02.2003 01:02:03.456 Indian/Cocos';
        create domain tbin binary default 'A';
        create domain tchr char(10) default 'QWERTYUIOP';
        create domain vbin varbinary(10) default x'deadbeef';
        create domain vchr_utf8 varchar(50) character set utf8 default _utf8 'նստի թախտին, սպասի բախտին' collate unicode_ci_ai; -- armenian
        create domain vchr_iso1 varchar(50) character set iso8859_1 default _iso8859_1 q'#Œil pour œil, dent pour dent#' collate fr_fr;
        create domain vchr_1250 varchar(50) character set win1250 default _win1250 q'#Každá liška svůj ocas chválí#' collate win_cz_ci_ai;
        create domain boo boolean default true;
        create domain bbin blob sub_type binary default x'deadbeef';
        create domain btxt blob sub_type text character set win1250 default _win1250 q'#Nie mów 'hop', póki nie przeskoczysz#' collate pxw_plk;
        commit;

        -- Every field of following ('source') table will be supplied with dedicated default value.
        -- But none of them  must present in the result of CTAS operation.
        -- Only default values from DOMAINS must be delivered in the target table.
        recreate table tbase(
            id016       id016     default 32767
           ,id032       id032     default 2147483647
           ,id064       id064     default 9223372036854775807
           ,id128       id128     default 170141183460469231731687303715884105727
           ,flt         flt       default 1e1
           ,dbl         dbl       default 1e1
           ,dec_05_0    dec_05_0  default 327.67
           ,dec_18_0    dec_18_0  default 123456789012345678
           ,dec_38_0    dec_38_0  default 12345678901234567890123456789012345678
           ,num_05_0    num_05_0  default 327.67
           ,num_18_0    num_18_0  default 123456789012345678
           ,num_38_0    num_38_0  default 12345678901234567890123456789012345678
           ,df_16       df_16     default 9.999999999999999E384
           ,df_34       df_34     default 9.999999999999999999999999999999999E6144
           ,dt          dt        default '30.12.9999'
           ,tm          tm        default '23:59:59.999'
           ,ts          ts        default '30.12.9999 23:59:59.999'
           ,tmtz        tmtz      default '23:59:59.999 Pacific/Fiji'
           ,tstz        tstz      default '30.12.9999 23:59:59.999 Pacific/Fiji'
           ,tbin        tbin      default 'B'
           ,tchr        tchr      default 'ASDFGHJKLZ'
           ,vbin        vbin      default x'BAADF00D'
           ,vchr_utf8   vchr_utf8 default 'արջը 7 երգ գիտի, 7ն էլ մեղրի մասին' -- armenian
           ,vchr_iso1   vchr_iso1 default q'#L'été, là-bas, ç'a été délicieux#'
           ,vchr_1250   vchr_1250 default q'#Nedělej z komára velblouda#'
           ,boo         boo       default false
           ,bbin        bbin      default x'BAADF00D'
           ,btxt        btxt      default 'Złej baletnicy przeszkadza rąbek u spódnicy'
        );

        recreate table ctas_permanent as (select * from tbase);
        set term ^; execute block as begin rdb$set_context('USER_SESSION','SHOW_FOR_TABLE', 'CTAS_PERMANENT'); end ^ set term ^;
        set count on;
        select * from v_fields_info;
    """

    act.expected_stdout = """
        RF_FLD_NAME ID016
        RF_FLD_SOURCE ID016
        RF_NOT_NULL <null>
        F_FLD_TYPE smallint
        F_FLD_PREC 0
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -32768
        RF_FLD_NAME ID032
        RF_FLD_SOURCE ID032
        RF_NOT_NULL <null>
        F_FLD_TYPE integer
        F_FLD_PREC 0
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -2147483648
        RF_FLD_NAME ID064
        RF_FLD_SOURCE ID064
        RF_NOT_NULL <null>
        F_FLD_TYPE bigint
        F_FLD_PREC 0
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -9223372036854775808
        RF_FLD_NAME ID128
        RF_FLD_SOURCE ID128
        RF_NOT_NULL <null>
        F_FLD_TYPE int128
        F_FLD_PREC 0
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -170141183460469231731687303715884105728
        RF_FLD_NAME FLT
        RF_FLD_SOURCE FLT
        RF_NOT_NULL <null>
        F_FLD_TYPE float
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -1e1
        RF_FLD_NAME DBL
        RF_FLD_SOURCE DBL
        RF_NOT_NULL <null>
        F_FLD_TYPE double precision
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -1e1
        RF_FLD_NAME DEC_05_0
        RF_FLD_SOURCE DEC_05_0
        RF_NOT_NULL <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 5
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -327.68
        RF_FLD_NAME DEC_18_0
        RF_FLD_SOURCE DEC_18_0
        RF_NOT_NULL <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 18
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -987654321098765432
        RF_FLD_NAME DEC_38_0
        RF_FLD_SOURCE DEC_38_0
        RF_NOT_NULL <null>
        F_FLD_TYPE decimal
        F_FLD_PREC 38
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -98765432109876543210987654321098765432
        RF_FLD_NAME NUM_05_0
        RF_FLD_SOURCE NUM_05_0
        RF_NOT_NULL <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 5
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -327.68
        RF_FLD_NAME NUM_18_0
        RF_FLD_SOURCE NUM_18_0
        RF_NOT_NULL <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 18
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -987654321098765432
        RF_FLD_NAME NUM_38_0
        RF_FLD_SOURCE NUM_38_0
        RF_NOT_NULL <null>
        F_FLD_TYPE numeric
        F_FLD_PREC 38
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -98765432109876543210987654321098765432
        RF_FLD_NAME DF_16
        RF_FLD_SOURCE DF_16
        RF_NOT_NULL <null>
        F_FLD_TYPE decfloat(16)
        F_FLD_PREC 16
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -9.999999999999999E384
        RF_FLD_NAME DF_34
        RF_FLD_SOURCE DF_34
        RF_NOT_NULL <null>
        F_FLD_TYPE decfloat(34)
        F_FLD_PREC 34
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default -9.999999999999999999999999999999999E6144
        RF_FLD_NAME DT
        RF_FLD_SOURCE DT
        RF_NOT_NULL <null>
        F_FLD_TYPE date
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default '01.02.2003'
        RF_FLD_NAME TM
        RF_FLD_SOURCE TM
        RF_NOT_NULL <null>
        F_FLD_TYPE time without time zone
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default '01:02:03.456'
        RF_FLD_NAME TS
        RF_FLD_SOURCE TS
        RF_NOT_NULL <null>
        F_FLD_TYPE timestamp without time zone
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default '01.02.2003 01:02:03.456'
        RF_FLD_NAME TMTZ
        RF_FLD_SOURCE TMTZ
        RF_NOT_NULL <null>
        F_FLD_TYPE time with time zone
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default '01:02:03.456 Indian/Cocos'
        RF_FLD_NAME TSTZ
        RF_FLD_SOURCE TSTZ
        RF_NOT_NULL <null>
        F_FLD_TYPE timestamp with time zone
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default '01.02.2003 01:02:03.456 Indian/Cocos'
        RF_FLD_NAME TBIN
        RF_FLD_SOURCE TBIN
        RF_NOT_NULL <null>
        F_FLD_TYPE binary
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 1
        CSET_NAME OCTETS
        BYTES_PER_C 1
        FLD_COLL OCTETS
        COLL_ATTR 1
        RF_DEFAULT_BLOB_ID <null>
        default 'A'
        RF_FLD_NAME TCHR
        RF_FLD_SOURCE TCHR
        RF_NOT_NULL <null>
        F_FLD_TYPE char
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 10
        CSET_NAME UTF8
        BYTES_PER_C 4
        FLD_COLL UTF8
        COLL_ATTR 1
        RF_DEFAULT_BLOB_ID <null>
        default 'QWERTYUIOP'
        RF_FLD_NAME VBIN
        RF_FLD_SOURCE VBIN
        RF_NOT_NULL <null>
        F_FLD_TYPE varbinary
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 10
        CSET_NAME OCTETS
        BYTES_PER_C 1
        FLD_COLL OCTETS
        COLL_ATTR 1
        RF_DEFAULT_BLOB_ID <null>
        default x'deadbeef'
        RF_FLD_NAME VCHR_UTF8
        RF_FLD_SOURCE VCHR_UTF8
        RF_NOT_NULL <null>
        F_FLD_TYPE varchar
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 50
        CSET_NAME UTF8
        BYTES_PER_C 4
        FLD_COLL UNICODE_CI_AI
        COLL_ATTR 7
        RF_DEFAULT_BLOB_ID <null>
        default _utf8 X'D5B6D5BDD5BFD5AB20D5A9D5A1D5ADD5BFD5ABD5B62C20D5BDD5BAD5A1D5BDD5AB20D5A2D5A1D5ADD5BFD5ABD5B6'
        RF_FLD_NAME VCHR_ISO1
        RF_FLD_SOURCE VCHR_ISO1
        RF_NOT_NULL <null>
        F_FLD_TYPE varchar
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 50
        CSET_NAME ISO8859_1
        BYTES_PER_C 1
        FLD_COLL FR_FR
        COLL_ATTR 1
        RF_DEFAULT_BLOB_ID <null>
        default _iso8859_1 X'C592696C20706F757220C593696C2C2064656E7420706F75722064656E74'
        RF_FLD_NAME VCHR_1250
        RF_FLD_SOURCE VCHR_1250
        RF_NOT_NULL <null>
        F_FLD_TYPE varchar
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN 50
        CSET_NAME WIN1250
        BYTES_PER_C 1
        FLD_COLL WIN_CZ_CI_AI
        COLL_ATTR 7
        RF_DEFAULT_BLOB_ID <null>
        default _win1250 X'4B61C5BE64C3A1206C69C5A16B61207376C5AF6A206F63617320636876C3A16CC3AD'
        RF_FLD_NAME BOO
        RF_FLD_SOURCE BOO
        RF_NOT_NULL <null>
        F_FLD_TYPE boolean
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default true
        RF_FLD_NAME BBIN
        RF_FLD_SOURCE BBIN
        RF_NOT_NULL <null>
        F_FLD_TYPE blob sub_type binary segment size 80
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME <null>
        BYTES_PER_C <null>
        FLD_COLL <null>
        COLL_ATTR <null>
        RF_DEFAULT_BLOB_ID <null>
        default x'deadbeef'
        RF_FLD_NAME BTXT
        RF_FLD_SOURCE BTXT
        RF_NOT_NULL <null>
        F_FLD_TYPE blob sub_type text segment size 80
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        F_CHR_LEN <null>
        CSET_NAME WIN1250
        BYTES_PER_C 1
        FLD_COLL PXW_PLK
        COLL_ATTR 1
        RF_DEFAULT_BLOB_ID <null>
        default _win1250 X'4E6965206DC3B3772027686F70272C2070C3B36B69206E69652070727A65736B6F637A79737A'
        Records affected: 28
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True, charset = 'utf8')
    assert act.clean_stdout == act.clean_expected_stdout
