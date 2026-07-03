#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. Basic test: check ability to use all data types.
DESCRIPTION:
    Test verifies that all existing data types can be used in CTAS, with boundary values for some of them.
    Also, we check that data in the source table and targets will be identical (using DISTINCT and COUNT).
NOTES:
    [03.07.2026] pzotov
    Difference in the SCALE for decimal and numeric columns between original and target tables may occur.
    Because of that, we have not to compare metadata definition for such columns.
    See: https://groups.google.com/g/firebird-devel/c/tp2UhWmljHU/m/tf-v5EHBAAAJ
    Checked on 6.0.0.2050
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
        recreate table tbase(
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
           ,tchr char(10)
           ,vbin varbinary(10)
           ,vchr_utf8 varchar(10) character set utf8 collate unicode_ci_ai
           ,vchr_1250 varchar(10) character set win1250 collate win_cz_ci_ai
           ,nchr nchar(10) -- iso8859-1
           ,vnch national char varying(10)
           ,boo boolean
           ,txt_0 blob sub_type 0
           ,txt_1 blob sub_type 1 character set win1250 collate win_cz
           ----------------------
           ,comp_01 computed by ( id016 - 1 )
           ,comp_02 computed by ( id032 - 1 )
           ,comp_03 computed by ( dt + 1 )
           ,comp_04 computed by ( extract(second from tm) )
           ,comp_05 computed by ( ts - 1 )
           ,comp_06 computed by ( reverse(vchr_utf8) )
           ,comp_07 computed by ( lower(vchr_1250) )
           ,comp_08 computed by ( lower(nchr) )
           ,comp_09 computed by ( upper(vnch) )
           ,comp_10 computed by ( not boo )
           ,comp_11 computed by ( octet_length(txt_0) )
           ,comp_12 computed by ( char_length(txt_1) )
        );
        commit;

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
           ,vchr_1250
           ,nchr
           ,vnch
           ,boo
           ,txt_0
           ,txt_1
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
           ,'A'
           ,'deadbeaf'
           ,'deadbeaf'
           ,'𒀂𒀃𒀄𒀅𒀆𒀇𒀈𒀉𒀊𒀋'
           ,'ŁŞŻŔĹĆÇČĘŮ'
           ,'ÁÂÃÄÅÆÇÈÉÊ'
           ,'çèéêëìíîïð'
           ,true
           ,(select list(gen_uuid(),'') from (select 1 x from rdb$types rows 100)) -- binary
           ,(select list( lpad('procházky Starým Městem', 100, uuid_to_char(gen_uuid())) , '') from (select 1 x from rdb$types rows 2)) -- win1250 collate win_cz
        );
        commit;

        SET AUTODDL OFF;
        commit;
        recreate table ctas_permanent as (select * from tbase) with data;
        recreate global temporary table ctas_gtt_sessn as (select * from ctas_permanent) with data ON COMMIT PRESERVE rows;
        recreate global temporary table ctas_gtt_trans as (select * from ctas_gtt_sessn) with data ON COMMIT DELETE rows;

        -- must be 1:
        select count(distinct ch) as count_ctas_blob
        from (
            select crypt_hash(txt_0 using sha512) || crypt_hash(txt_1 using sha512) as ch from tbase
            UNION ALL
            select crypt_hash(txt_0 using sha512) || crypt_hash(txt_1 using sha512) from ctas_permanent
            UNION ALL
            select crypt_hash(txt_0 using sha512) || crypt_hash(txt_1 using sha512) from ctas_gtt_sessn
            UNION ALL
            select crypt_hash(txt_0 using sha512) || crypt_hash(txt_1 using sha512) from ctas_gtt_trans
        );

        update ctas_permanent set
            txt_0 = null
           ,txt_1 = null
        ;
        recreate global temporary table ctas_gtt_sessn as (select * from ctas_permanent) with data ON COMMIT PRESERVE rows;
        recreate global temporary table ctas_gtt_trans as (select * from ctas_gtt_sessn) with data ON COMMIT DELETE rows;

        -- all must be 1:
        select count(*) as count_ctas_perm from ctas_permanent;
        select count(*) as count_ctas_gtts from ctas_gtt_sessn;
        select count(*) as count_ctas_gttt from ctas_gtt_trans;

        -- must be 1:
        select count(*) as count_ctas_uniq
        from (
            select distinct * from ctas_permanent
            UNION DISTINCT
            select distinct * from ctas_gtt_sessn
            UNION DISTINCT
            select distinct * from ctas_gtt_trans
        );

    """

    act.expected_stdout = """
        COUNT_CTAS_BLOB 1
        COUNT_CTAS_PERM 1
        COUNT_CTAS_GTTS 1
        COUNT_CTAS_GTTT 1
        COUNT_CTAS_UNIQ 1
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True, charset = 'utf8')
    assert act.clean_stdout == act.clean_expected_stdout
