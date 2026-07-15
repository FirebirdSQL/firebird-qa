#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. NUMERICAL TYPES. Check content of RDB$ tables for a CTAS-table when fields are expressions, literals or aggregates.
DESCRIPTION:
    $FB_HOME/doc/sql.extensions/README.create_table_as_query.md:
        ## Datatypes and Domains
        ...
        For any other select list item (an expression, a literal, or an aggregate, for example), the new column's
        datatype  is derived from the QUERY RESULT.
NOTES:
    [16.07.2026] pzotov
        This test checks only NUMERICAL TYPES.

        Difference existed in the SCALE for decimal/numeric columns between original and target tables.
        Fixed in #6c797c76f (06-JUL-2026 11:22+0000).
        See: https://groups.google.com/g/firebird-devel/c/tp2UhWmljHU/m/tf-v5EHBAAAJ
        See also #7df850dd ("Fix some field precision of CTAS").

        NOTE. To make comparison between 'old' and 'new' outputs easier, one may to change following in the script:
            * comment out 'set list on;'
            * temporary set substitutions = []
            * temporary set act.expected_stdout = ''.
        Checked on 6.0.0.2074-7df850d.
"""
import pytest
from firebird.qa import *

db = db_factory(charset = 'utf8')

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_script = f"""
        set bail on;
        set blob all;
        set list on;
        set autoterm on;
        set autoddl off;
        create sequence g;
        commit;
        execute block as begin rdb$set_context('USER_SESSION','SHOW_FOR_TABLE', 'CTAS_TEST'); end;

        create view v_fields_info as
        select
            rf.rdb$field_name as rf_fld_name
            ,f.rdb$field_type as f_field_type
            ,f.rdb$field_sub_type as f_fld_sub_type
            ,f.rdb$field_precision as f_fld_prec
            ,f.rdb$field_scale as f_fld_scale
        from rdb$relation_fields rf
        join rdb$fields f on rf.rdb$field_source = f.rdb$field_name
        where rf.rdb$relation_name = coalesce( rdb$get_context('USER_SESSION','SHOW_FOR_TABLE'), upper('CTAS_TEST'))
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

        create domain dm_016 smallint;
        create domain dm_032 int;
        create domain dm_064 bigint;
        create domain dm_128 int128;

        create domain dm_flo float;
        create domain dm_dbl double precision;

        create domain dm_dec_01 decimal(1);
        create domain dm_dec_04 decimal(4);
        create domain dm_dec_04_04 decimal(4,4);
        create domain dm_dec_05 decimal(5);
        create domain dm_dec_09 decimal(9);
        create domain dm_dec_09_09 decimal(9,9);
        create domain dm_dec_10 decimal(10);
        create domain dm_dec_18 decimal(18);
        create domain dm_dec_18_18 decimal(18,18);
        create domain dm_dec_19 decimal(19);
        create domain dm_dec_38 decimal(38);
        create domain dm_dec_38_38 decimal(38,38);

        create domain dm_num_01 numeric(1);
        create domain dm_num_04 numeric(4);
        create domain dm_num_04_04 numeric(4,4);
        create domain dm_num_05 numeric(5);
        create domain dm_num_09 numeric(9);
        create domain dm_num_09_09 numeric(9,9);
        create domain dm_num_10 numeric(10);
        create domain dm_num_18 numeric(18);
        create domain dm_num_18_18 numeric(18,18);
        create domain dm_num_19 numeric(19);
        create domain dm_num_38 numeric(38);
        create domain dm_num_38_38 numeric(38,38);

        create domain dm_df16 decfloat(16);
        create domain dm_df34 decfloat(34);

        recreate table tbase (
             dm_016     dm_016
            ,dm_032     dm_032
            ,dm_064     dm_064
            ,dm_128     dm_128

            ,dm_flo     dm_flo
            ,dm_dbl     dm_dbl

            ,dm_dec_01  dm_dec_01
            ,dm_dec_04  dm_dec_04
            ,dm_dec_04_04  dm_dec_04_04
            ,dm_dec_05  dm_dec_05
            ,dm_dec_09  dm_dec_09
            ,dm_dec_09_09  dm_dec_09_09
            ,dm_dec_10  dm_dec_10
            ,dm_dec_18  dm_dec_18
            ,dm_dec_18_18  dm_dec_18_18
            ,dm_dec_19  dm_dec_19
            ,dm_dec_38  dm_dec_38
            ,dm_dec_38_38  dm_dec_38_38

            ,dm_num_01  dm_num_01
            ,dm_num_04  dm_num_04
            ,dm_num_04_04  dm_num_04_04
            ,dm_num_05  dm_num_05
            ,dm_num_09  dm_num_09
            ,dm_num_09_09  dm_num_09_09
            ,dm_num_10  dm_num_10
            ,dm_num_18  dm_num_18
            ,dm_num_18_18  dm_num_18_18
            ,dm_num_19  dm_num_19
            ,dm_num_38  dm_num_38
            ,dm_num_38_38  dm_num_38_38

            ,dm_df16    dm_df16
            ,dm_df34    dm_df34
        );

        -- ####################################
        -- ###   e x p r e s s i o n s - 1  ###
        -- ####################################
        -- case-1: based on DOMAINS.
        -- "... the new column's datatype is derived from the query result."
        -- /*
        recreate table ctas_test as (
            select
                cast(null as dm_016) as expr_016
                ,cast(null as dm_032) as expr_032
                ,cast(null as dm_064) as expr_064
                ,cast(null as dm_128) as expr_128

                ,cast(null as dm_flo) as expr_flo
                ,cast(null as dm_dbl) as expr_dbl

                ,cast(null as dm_dec_01) as expr_dec_01
                ,cast(null as dm_dec_04) as expr_dec_04
                ,cast(null as dm_dec_04_04) as expr_dec_04_04
                ,cast(null as dm_dec_05) as expr_dec_05
                ,cast(null as dm_dec_09) as expr_dec_09
                ,cast(null as dm_dec_09_09) as expr_dec_09_09
                ,cast(null as dm_dec_10) as expr_dec_10
                ,cast(null as dm_dec_18) as expr_dec_18
                ,cast(null as dm_dec_18_18) as expr_dec_18_18
                ,cast(null as dm_dec_19) as expr_dec_19
                ,cast(null as dm_dec_38) as expr_dec_38
                ,cast(null as dm_dec_38_38) as expr_dec_38_38

                ,cast(null as dm_num_01) as expr_num_01
                ,cast(null as dm_num_04) as expr_num_04
                ,cast(null as dm_num_04_04) as expr_num_04_04
                ,cast(null as dm_num_05) as expr_num_05
                ,cast(null as dm_num_09) as expr_num_09
                ,cast(null as dm_num_09_09) as expr_num_09_09
                ,cast(null as dm_num_10) as expr_num_10
                ,cast(null as dm_num_18) as expr_num_18
                ,cast(null as dm_num_18_18) as expr_num_18_18
                ,cast(null as dm_num_19) as expr_num_19
                ,cast(null as dm_num_38) as expr_num_38
                ,cast(null as dm_num_38_38) as expr_num_38_38

                ,cast(null as dm_df16) as expr_df16
                ,cast(null as dm_df34) as expr_df34
            from rdb$database
        );
        commit;
        select * from v_fields_info;
        -- */

        -- ###################################
        -- ###   e x p r e s s i o n s - 2 ###
        -- ###################################
        -- case-2: results of complex arithmetic evaluations
        -- "... the new column's datatype is derived from the query result."
        -- /*
        recreate table ctas_test as (
            select
                  -  + 025  as eval_001
                ,- - - -003 as eval_002
                ,-41- (- (12)  +27)                                                                               as eval_003 --        -56
                ,-(-((((21))))-((176)))-(-(-(113)-((-(-(219))))))                                                 as eval_004 --       -135
                ,(((((7+8)/(3+2)+5)/9)+(29+3)/2+(7+6)*4)+29/(45+3))                                               as eval_005 --         68
                ,10450090/(2+19040000/(2+1954321/(2+1748159/(2+167349/(2+16184/(2+1337/(2+137/(2+17/(2+1))))))))) as eval_006 --        412 ?
                ,-1396417113/(-5-(-9)/(-233333333/(-111)))/((-37)-(-19)*(-33)-(-29))                              as eval_007 --    -439816
                ,8*-9/41                                                                                          as eval_008 --    0 or -1 ?
                ,8*9/-41                                                                                          as eval_009 --        -1
                ,347/-19*4/-3                                                                                     as eval_010 --     13 or 24 ?
                ,347/19*-6/-2                                                                                     as eval_011 --         54
                ,347/-17*-4/-3                                                                                    as eval_012 --    -20 or -26 ?
                ,347/17*-6*-5/-2                                                                                  as eval_013 --  -240 or -300 ?
                ,7951*-229*+-7                                                                                    as eval_014 --  12745453
                ,4233199/-41*7/-(-41)                                                                             as eval_015 --  -604742 or -29632393/1681 = 17627 ?
                ,757863/-319*57/- -23                                                                             as eval_016 --       -959
                ,2291737/-(-28)*3                                                                                 as eval_017 --      27282
                ,973679137/-(719)/-19                                                                             as eval_018 --   26315652
                ,65535/-+-55/3                                                                                    as eval_019 --       3640
                ,((55+66) * 13 +47)/((33+44)+9)/2*(500/2/3/(4+9))                                                 as eval_020 --         54
                ,(9-(8-(7-(6-5))))-(-(1-(2-3)*9)/2-((5-2)*3+7)*4)                                                 as eval_021 --         76
                ,((5+(3/(-2)))+(4*(-3)))                                                                          as eval_022 --         -8
                ,3+1/(7+1/(5*3+1/(1+1/((4*(9*8+1))))))                                                            as eval_023 --          3
                ,((-7)-(-(-(-(211)+27)-(-9))) )/(-3)                                                              as eval_024 --        -62
                ,(-(-49)-(-((-(-(-(-(-2)-37)-(-7-(-(3)))))))))/(-2)                                               as eval_025 --        -44
                ,((-(-(797739/-(32-55))-7)/2))/(-(-1137)/(-32/-9))                                                as eval_026 --         45
                ,((-9)-(-((-(-(-(-(2)+19)-(-2)))))))/(-2)                                                         as eval_027 --         12
                ,(((-9))-(-((-(-(-(((-(2)+17)))-(-2)))))))/(-2)                                                   as eval_028 --         11
                ,- -((- - -(-(- -(((- - -((-(1197-19/(-(-(-13)-(-3)))+(-61-(-24))))))))))))                       as eval_029 --       1161
                ,(-(-((-39191-(-9))/(- -4))*(-19-(-11))*((-6)-8)*(- -6- -7)/2))                                   as eval_030 --   -7130760
                ,213067*(((-3))-(-((((-((-(-(((-(3)+16)))-(-7))))))))))/(-2)                                      as eval_031 --     958801 
                ,2147483647/( (135-(-273/(-11)))/7*(213-(-(-(-852/117)/(-92))))/7*(21-19/7+37/9)*(37-48/6-29/3-37/7-27/9)*(14-(-3-(-2-(-3-(-2))))) * (91-779/(191+49-(-9))-(-(-(-(-(-11-(-(-(-(-(-10))))))))))) )*(1000008000-999999937)*(2000000030-1999999916)*(-11-(-3)-(-9)-(-7-(-4)))*((-17-(-3)-(-9)-(-12-(-4)))*(19-34/2))*(((((((((10000000+9)/7+8 )/3+29)/4+ 16)/9+17)/6+18)/3+19)/8/3-1)/7)
                 as eval_032 -- 970656192
                ,2147483647/( (733-(-134/(-83)))/7*(219-(-(-(-619/347)/(-73))))/3*(13-13/7+19/3)*(17-78/6-21/3-39/3-29/7)*(28-(-3-(-2-(-3-(-2))))) * (16-777/(91+41-(-9))-(-(-(-(-(-11-(-(-(-(-(-10))))))))))))*(1000000000-999999997)*(2000000000-1999999996)*(-10-(-3)-(-9)-(-7-(-4)))*((-77-(-3)-(-9)-(-12-(-4)))*(19-31/2))*(((((((((10800900+9)/2+8 )/13+15999774)/141+ 16)/5+17)/6+198)/7+19)/3/5-1)/7)*(((-4))-(-((((-((-(-(((-(2)+16)))-(-2))))))))))/(-2)*(-3-(-9-(-8-(-7-(-6-(-5))))))/(-9-(-2-(-3-(-4))))/(-739-(-511))-(-1947777/(-31))
                 as eval_033 -- -59631
            from rdb$database
        );
        commit;
        select * from v_fields_info;
        select * from ctas_test;
        commit;
        -- */

        -- ##############################
        -- ###   a g g r e g a t e s  ###
        -- ##############################
        -- "... the new column's datatype is derived from the query result."
        -- /*
        recreate table ctas_test as (
            select
                min(dm_016) as agg_016
                ,min(dm_032) as agg_032
                ,min(dm_064) as agg_064
                ,min(dm_128) as agg_128

                ,min(dm_flo) as agg_flo
                ,min(dm_dbl) as agg_dbl

                ,min(dm_dec_01) as agg_dec_01
                ,min(dm_dec_04) as agg_dec_04
                ,min(dm_dec_04_04) as agg_dec_04_04
                ,min(dm_dec_05) as agg_dec_05
                ,min(dm_dec_09) as agg_dec_09
                ,min(dm_dec_09_09) as agg_dec_09_09
                ,min(dm_dec_10) as agg_dec_10
                ,min(dm_dec_18) as agg_dec_18
                ,min(dm_dec_18_18) as agg_dec_18_18
                ,min(dm_dec_19) as agg_dec_19
                ,min(dm_dec_38) as agg_dec_38
                ,min(dm_dec_38_38) as agg_dec_38_38

                ,min(dm_num_01) as agg_num_01
                ,min(dm_num_04) as agg_num_04
                ,min(dm_num_04_04) as agg_num_04_04
                ,min(dm_num_05) as agg_num_05
                ,min(dm_num_09) as agg_num_09
                ,min(dm_num_09_09) as agg_num_09_09
                ,min(dm_num_10) as agg_num_10
                ,min(dm_num_18) as agg_num_18
                ,min(dm_num_18_18) as agg_num_18_18
                ,min(dm_num_19) as agg_num_19
                ,min(dm_num_38) as agg_num_38
                ,min(dm_num_38_38) as agg_num_38_38

                ,min(dm_df16) as agg_df16
                ,min(dm_df34) as agg_df34
            from tbase
        );
        commit;
        select * from v_fields_info;
        -- */

        -- ###########################
        -- ###   l i t e r a l s   ###
        -- ###########################
        -- "... the new column's datatype is derived from the query result."
        --/*
        recreate table ctas_test as (
            select
                 0 as lit_016                                             -- 496 long
                ,2147483647 as lit_032                                    -- 496 long
                ,9223372036854775807 as lit_064                           -- 580 int64
                ,170141183460469231731687303715884105727 as lit_128       -- 32752 int128
                ,1e1 as lit_dbl                                           -- 480 double
                ,1.0 as lit_num_01_01                                     -- 580 scale=-1
                ,.0001 as lit_num_04_04                                   -- 580 scale=-4
                ,.00001 as lit_num_05_05                                  -- 580 scale=-5
                ,.000000001 as lit_num_09_09                              -- 580 scale=-9
                ,.0000000001 as lit_num_10_10                             -- 580 scale=-10
                ,.000000000000000001 as lit_num_18_18                     -- 580 scale=-18
                ,.00000000000000000000000000000000000001 as lit_num_38_38 -- 580 scale=-38
                ,1e-309 as lit_df34                                       -- 32762 decfloat
             from rdb$database
        );
        commit;
        select * from v_fields_info;
        select * from ctas_test;
        commit;
        -- */

        -- ##################################
        -- ###   s c a l a r   f u n c s  ###
        -- ##################################
        -- check result of some functions that do not require any fields from source:
        -- "... the new column's datatype is derived from the query result."
        --/*
        recreate table ctas_test as (
            select
                gen_id(g,1) as scal_gen_id
                ,rand() as scal_rand
                ,gen_uuid() as scal_uuid
                ,sign(pi()) as scal_sign
                ,pi() as scal_pi
                ,exp(pi()) as scal_exp
                ,normalize_decfloat(0E-6176) as scal_norm_df
                ,rdb$get_context('SYSTEM', 'DB_NAME') as scal_dbnm
                ,hash(rdb$get_context('SYSTEM', 'DB_NAME')) as scal_hash
                ,crypt_hash (rdb$get_context('SYSTEM', 'DB_NAME') using sha512) as scal_cryp
                ,rsa_private(256) as scal_rsap
                ,hex_encode(gen_uuid()) as scal_hexe
                ,first_day(of month from current_date) as scal_day1
                ,blob_append(null, '') as scal_blob_app
            from rdb$database
        );
        commit;
        select * from v_fields_info;
        --*/
    """

    act.expected_stdout = """
        RF_FLD_NAME EXPR_016
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_032
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_064
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_128
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_FLO
        F_FIELD_TYPE 10
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DBL
        F_FIELD_TYPE 27
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_01
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_04
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_04_04
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE -4
        RF_FLD_NAME EXPR_DEC_05
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_09
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_09_09
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE -9
        RF_FLD_NAME EXPR_DEC_10
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 18
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 18
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_18_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 18
        F_FLD_SCALE -18
        RF_FLD_NAME EXPR_DEC_19
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 38
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_38
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 38
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DEC_38_38
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 38
        F_FLD_SCALE -38
        RF_FLD_NAME EXPR_NUM_01
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 4
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_NUM_04
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 4
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_NUM_04_04
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 4
        F_FLD_SCALE -4
        RF_FLD_NAME EXPR_NUM_05
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_NUM_09
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_NUM_09_09
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 9
        F_FLD_SCALE -9
        RF_FLD_NAME EXPR_NUM_10
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 18
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_NUM_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 18
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_NUM_18_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 18
        F_FLD_SCALE -18
        RF_FLD_NAME EXPR_NUM_19
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 38
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_NUM_38
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 38
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_NUM_38_38
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 38
        F_FLD_SCALE -38
        RF_FLD_NAME EXPR_DF16
        F_FIELD_TYPE 24
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC 16
        F_FLD_SCALE 0
        RF_FLD_NAME EXPR_DF34
        F_FIELD_TYPE 25
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC 34
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_001
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_002
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_003
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_004
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_005
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_006
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_007
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_008
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_009
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_010
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_011
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_012
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_013
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_014
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_015
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_016
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_017
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_018
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_019
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_020
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_021
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_022
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_023
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_024
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_025
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_026
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_027
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_028
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_029
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_030
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_031
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_032
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME EVAL_033
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        EVAL_001 -25
        EVAL_002 3
        EVAL_003 -56
        EVAL_004 -135
        EVAL_005 68
        EVAL_006 412
        EVAL_007 -439816
        EVAL_008 -1
        EVAL_009 -1
        EVAL_010 24
        EVAL_011 54
        EVAL_012 -26
        EVAL_013 -300
        EVAL_014 12745453
        EVAL_015 -17627
        EVAL_016 -5885
        EVAL_017 245541
        EVAL_018 71274
        EVAL_019 397
        EVAL_020 54
        EVAL_021 76
        EVAL_022 -8
        EVAL_023 3
        EVAL_024 -62
        EVAL_025 -44
        EVAL_026 45
        EVAL_027 12
        EVAL_028 11
        EVAL_029 1161
        EVAL_030 -7130760
        EVAL_031 958801
        EVAL_032 970656192
        EVAL_033 -59631
        RF_FLD_NAME AGG_016
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_032
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_064
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_128
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_FLO
        F_FIELD_TYPE 10
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DBL
        F_FIELD_TYPE 27
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_01
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_04
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_04_04
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE -4
        RF_FLD_NAME AGG_DEC_05
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_09
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_09_09
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 9
        F_FLD_SCALE -9
        RF_FLD_NAME AGG_DEC_10
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 18
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 18
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_18_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 18
        F_FLD_SCALE -18
        RF_FLD_NAME AGG_DEC_19
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 38
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_38
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 38
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DEC_38_38
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 2
        F_FLD_PREC 38
        F_FLD_SCALE -38
        RF_FLD_NAME AGG_NUM_01
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 4
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_NUM_04
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 4
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_NUM_04_04
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 4
        F_FLD_SCALE -4
        RF_FLD_NAME AGG_NUM_05
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_NUM_09
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 9
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_NUM_09_09
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 9
        F_FLD_SCALE -9
        RF_FLD_NAME AGG_NUM_10
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 18
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_NUM_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 18
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_NUM_18_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 18
        F_FLD_SCALE -18
        RF_FLD_NAME AGG_NUM_19
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 38
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_NUM_38
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 38
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_NUM_38_38
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 1
        F_FLD_PREC 38
        F_FLD_SCALE -38
        RF_FLD_NAME AGG_DF16
        F_FIELD_TYPE 24
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC 16
        F_FLD_SCALE 0
        RF_FLD_NAME AGG_DF34
        F_FIELD_TYPE 25
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC 34
        F_FLD_SCALE 0
        RF_FLD_NAME LIT_016
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME LIT_032
        F_FIELD_TYPE 8
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME LIT_064
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME LIT_128
        F_FIELD_TYPE 26
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME LIT_DBL
        F_FIELD_TYPE 27
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME LIT_NUM_01_01
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE -1
        RF_FLD_NAME LIT_NUM_04_04
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE -4
        RF_FLD_NAME LIT_NUM_05_05
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE -5
        RF_FLD_NAME LIT_NUM_09_09
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE -9
        RF_FLD_NAME LIT_NUM_10_10
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE -10
        RF_FLD_NAME LIT_NUM_18_18
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE -18
        RF_FLD_NAME LIT_NUM_38_38
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE -38
        RF_FLD_NAME LIT_DF34
        F_FIELD_TYPE 25
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC 34
        F_FLD_SCALE 0
        LIT_016 0
        LIT_032 2147483647
        LIT_064 9223372036854775807
        LIT_128 170141183460469231731687303715884105727
        LIT_DBL 10.00000000000000
        LIT_NUM_01_01 1.0
        LIT_NUM_04_04 0.0001
        LIT_NUM_05_05 0.00001
        LIT_NUM_09_09 0.000000001
        LIT_NUM_10_10 0.0000000001
        LIT_NUM_18_18 0.000000000000000001
        LIT_NUM_38_38 000000000000000000001
        LIT_DF34 1E-309
        RF_FLD_NAME SCAL_GEN_ID
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_RAND
        F_FIELD_TYPE 27
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_UUID
        F_FIELD_TYPE 14
        F_FLD_SUB_TYPE 0
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_SIGN
        F_FIELD_TYPE 7
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_PI
        F_FIELD_TYPE 27
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_EXP
        F_FIELD_TYPE 27
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_NORM_DF
        F_FIELD_TYPE 25
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC 34
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_DBNM
        F_FIELD_TYPE 37
        F_FLD_SUB_TYPE 0
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_HASH
        F_FIELD_TYPE 16
        F_FLD_SUB_TYPE 0
        F_FLD_PREC 0
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_CRYP
        F_FIELD_TYPE 37
        F_FLD_SUB_TYPE 0
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_RSAP
        F_FIELD_TYPE 37
        F_FLD_SUB_TYPE 0
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_HEXE
        F_FIELD_TYPE 37
        F_FLD_SUB_TYPE 0
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_DAY1
        F_FIELD_TYPE 12
        F_FLD_SUB_TYPE <null>
        F_FLD_PREC <null>
        F_FLD_SCALE 0
        RF_FLD_NAME SCAL_BLOB_APP
        F_FIELD_TYPE 261
        F_FLD_SUB_TYPE 1
        F_FLD_PREC <null>
        F_FLD_SCALE 0
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True, charset = 'utf8')
    assert act.clean_stdout == act.clean_expected_stdout
