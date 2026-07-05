#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8974
TITLE:       Temporary Tables in Packages (#8974) - basic test.
DESCRIPTION:
    Test verifies ability to create packages with public and private temporary tables at connection- or transaction- level.
    Every PTT (package temporary table) will have two columns: ID (identifier, int) and F01 ('custom') which type is taken
    from the set of all existing FB datatypes (see 'types_map').
    Every package will have one public temporary table (declared in its header) and two private tables (declared in its body).
    Also, package has public procedures to fill some data in each PTT and show it then: 'sp_***_fill' and 'sp_***show'.
    After data is written to PTT, we call 'sp_***show' and compare obtained data with expected.
NOTES:
    [05.07.2026] pzotov
    Problem was encountered (FB crash) if we do commit after every checked datatype (see below: 'xxx con.commit() xxx').
    If we skip commit then all fine.
    See also: https://groups.google.com/g/firebird-devel/c/azqX6VgM59k/m/oOkRbGaLAQAJ
    WAITING FOR FIX!

    Checked on 6.0.0.2060-637102f.
"""

import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, DatabaseError

db = db_factory(init = 'create sequence g; commit;')
act = python_act('db')

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    with act.db.connect(charset = 'utf8') as con:
        cur = con.cursor()

        # 1. Check ability to declare package temp. tables with columns of all existing datatype:
        # Examples from gh_8950_test.py:
        # ------------------------------
        types_map = {
            't_boo' : ('boolean'                  , ( 'false', 'true' ) ) # see README.packages.txt: "Bool As Value"
           ,'t_sml' : ('smallint'                 , ( '-32768', '32767' ) )
           ,'t_int' : ('int'                      , ( '-2147483648', '2147483647' ) )
           ,'t_big' : ('bigint'                   , ( '-9223372036854775808', '9223372036854775807' ) )
           ,'t_128' : ('int128'                   , ( '-170141183460469231731687303715884105728', '170141183460469231731687303715884105727' ) )
           ,'t_flt' : ('float'                    , ( '3.40282346638e38', '1.40129846432e-45', '1.17549435082e-38' ) )
           ,'t_dbl' : ('double precision'         , ( '-3e-308', '3e-308', '1.7976931348623157e308', '-9007199254740992', '9007199254740992' ) ) # NOT YET ALLOWED, see gh-8647: '4.9406564584124e-324', '2.2250738585072009e-308',
           ,'t_num' : ('numeric(2,2)'             , ( '-327.68', '327.67' ) )
           ,'t_dec' : ('decimal(2,2)'             , ( '-327.68', '327.67' ) )
           ,'t_dfl' : ('decfloat'                 , ( '-9.999999999999999999999999999999999E6144', '-1.0E-6143', '1.0E-6143', '9.999999999999999999999999999999999E6144', '0E-6144' ) )
           ,'t_dat' : ('date'                     , ( "'29.02.2004'", ) )
           ,'t_tim' : ('time'                     , ( "'01:02:03.456'", ) )
           ,'t_tms' : ('timestamp'                , ( "'29.02.2004 01:02:03.456'", ) )
           ,'t_tmz' : ('time with time zone'      , ( "'01:02:03.456 Indian/Cocos'", ) )
           ,'t_tsz' : ('timestamp with time zone' , ( "'29.02.2004 01:02:03.456 Indian/Cocos'", ) )
           ,'t_vchr_utf8_regular'    : ('varchar(255) character set utf8',  ("'შობას გილოცავთ'",) )         # georgian
           ,'t_vchr_utf8_ci_ai'      : ('varchar(255) character set utf8 collate unicode_ci_ai',  ("'Շնորհավոր Սուրբ Ծնունդ'",) ) # armenian
           ,'t_vchr_iso8859_1_da_da' : ('varchar(255) character set iso8859_1 collate da_da',  ("q'#Børn får søde gærøl#'",)  )
           ,'t_vchr_iso8859_1_de_de' : ('varchar(255) character set iso8859_1 collate de_de',  ("q'#Müßiggänger müssen süße Äpfel grüßen#'",)  )
           ,'t_vchr_iso8859_1_fr_fr' : ('varchar(255) character set iso8859_1 collate fr_fr',  ("q'#L'été, là-bas, ç'a été délicieux#'",)  )
           ,'t_blb_utf8_regular'     : ('blob sub_type text character set utf8',  ("'შობას გილოცავთ'",) )   # georgian
           ,'t_blb_utf8_ci_ai'       : ('blob sub_type text character set utf8 collate unicode_ci_ai',  ("'Շնորհավոր Սուրբ Ծնունդ'",) ) # armenian
        }

        for k, v in types_map.items():
            decl_type = v[0]
            check_lst = v[1]

            ddl_pkg_head = f"""
                create or alter package pg_temp_tab as
                begin
                    temporary table {k}_pub(id int, f01 {decl_type}) on commit preserve rows unique index {k}_pub_unq(id);
                    procedure sp_{k}_fill;
                    function fn_{k}_count returns int;
                    procedure sp_{k}_show returns(src varchar(255), id int, f01 {decl_type});
                end

            """

            dml_pub_fill = '\n'.join( [f'insert into {k}_pub(id, f01) values(gen_id(g,1), {x});' for x in check_lst] )
            dml_priv_fill = '\n'.join( [f'insert into {k}_priv_att(id, f01) values(-gen_id(g,1), {x});' for x in check_lst] )
            ddl_pkg_body = f"""
                recreate package body pg_temp_tab as
                begin
                    temporary table {k}_priv_att(id int, f01 {decl_type}) on commit preserve rows unique index {k}_priv_unq(id);
                    temporary table {k}_priv_trn(id int, f01 {decl_type}) unique desc index {k}_priv_trn_unq(id);
                    procedure sp_{k}_fill as
                    begin
                        {dml_priv_fill}
                        {dml_pub_fill}
                        insert into {k}_priv_trn(id, f01) select -gen_id(g,1), f01 from {k}_priv_att;
                    end
                    
                    function fn_{k}_count returns int as
                    begin
                        return (select count(*) from {k}_pub) + (select count(*) from {k}_priv_att) + (select count(*) from {k}_priv_trn);
                    end

                    procedure sp_{k}_show returns(src varchar(255), id int, f01 {decl_type}) as
                    begin
                        for
                            select '{k}_pub' as src, id, f01 from {k}_pub
                            UNION ALL
                            select '{k}_priv_att' as src, id, f01 from {k}_priv_att
                            UNION ALL
                            select '{k}_priv_trn' as src, id, f01 from {k}_priv_trn
                        as cursor c
                        do begin
                            src = c.src;
                            id = c.id;
                            f01 = c.f01;
                            suspend;
                        end
                    end
                end

            """
            
            con.execute_immediate(ddl_pkg_head)
            con.execute_immediate(ddl_pkg_body)

            cur.callproc(f'pg_temp_tab.sp_{k}_fill')
            #cur.execute(f'select pg_temp_tab.fn_{k}_count() as "fn_{k}_count" from rdb$database')
            cur.execute(f'select * from pg_temp_tab.sp_{k}_show')
            ccol=cur.description
            for r in cur:
                for i in range(0,len(ccol)):
                    print( ccol[i][0],':', r[i])

            # 05.07.2026. ::: ACHTUNG :::
            # FOLLOWING COMMIT MUST BE COMMENTED OUT!
            # OTHERWISE FB CRASHES, SEE
            # https://groups.google.com/g/firebird-devel/c/azqX6VgM59k/m/oOkRbGaLAQAJ
            # WAITING FOR FIX!
            # xxx con.commit() xxx

        # < for k, v in types_map.items()

    act.expected_stdout = f"""
        SRC : t_boo_pub
        ID : 3
        F01 : False
        SRC : t_boo_pub
        ID : 4
        F01 : True
        SRC : t_boo_priv_att
        ID : -1
        F01 : False
        SRC : t_boo_priv_att
        ID : -2
        F01 : True
        SRC : t_boo_priv_trn
        ID : -5
        F01 : False
        SRC : t_boo_priv_trn
        ID : -6
        F01 : True

        SRC : t_sml_pub
        ID : 9
        F01 : -32768
        SRC : t_sml_pub
        ID : 10
        F01 : 32767
        SRC : t_sml_priv_att
        ID : -7
        F01 : -32768
        SRC : t_sml_priv_att
        ID : -8
        F01 : 32767
        SRC : t_sml_priv_trn
        ID : -11
        F01 : -32768
        SRC : t_sml_priv_trn
        ID : -12
        F01 : 32767

        SRC : t_int_pub
        ID : 15
        F01 : -2147483648
        SRC : t_int_pub
        ID : 16
        F01 : 2147483647
        SRC : t_int_priv_att
        ID : -13
        F01 : -2147483648
        SRC : t_int_priv_att
        ID : -14
        F01 : 2147483647
        SRC : t_int_priv_trn
        ID : -17
        F01 : -2147483648
        SRC : t_int_priv_trn
        ID : -18
        F01 : 2147483647

        SRC : t_big_pub
        ID : 21
        F01 : -9223372036854775808
        SRC : t_big_pub
        ID : 22
        F01 : 9223372036854775807
        SRC : t_big_priv_att
        ID : -19
        F01 : -9223372036854775808
        SRC : t_big_priv_att
        ID : -20
        F01 : 9223372036854775807
        SRC : t_big_priv_trn
        ID : -23
        F01 : -9223372036854775808
        SRC : t_big_priv_trn
        ID : -24
        F01 : 9223372036854775807

        SRC : t_128_pub
        ID : 27
        F01 : -170141183460469231731687303715884105728
        SRC : t_128_pub
        ID : 28
        F01 : 170141183460469231731687303715884105727
        SRC : t_128_priv_att
        ID : -25
        F01 : -170141183460469231731687303715884105728
        SRC : t_128_priv_att
        ID : -26
        F01 : 170141183460469231731687303715884105727
        SRC : t_128_priv_trn
        ID : -29
        F01 : -170141183460469231731687303715884105728
        SRC : t_128_priv_trn
        ID : -30
        F01 : 170141183460469231731687303715884105727

        SRC : t_flt_pub
        ID : 34
        F01 : 3.4028234663852886e+38
        SRC : t_flt_pub
        ID : 35
        F01 : 1.401298464324817e-45
        SRC : t_flt_pub
        ID : 36
        F01 : 1.1754943508222875e-38
        SRC : t_flt_priv_att
        ID : -31
        F01 : 3.4028234663852886e+38
        SRC : t_flt_priv_att
        ID : -32
        F01 : 1.401298464324817e-45
        SRC : t_flt_priv_att
        ID : -33
        F01 : 1.1754943508222875e-38
        SRC : t_flt_priv_trn
        ID : -37
        F01 : 3.4028234663852886e+38
        SRC : t_flt_priv_trn
        ID : -38
        F01 : 1.401298464324817e-45
        SRC : t_flt_priv_trn
        ID : -39
        F01 : 1.1754943508222875e-38

        SRC : t_dbl_pub
        ID : 45
        F01 : -2.9999999999999997e-308
        SRC : t_dbl_pub
        ID : 46
        F01 : 2.9999999999999997e-308
        SRC : t_dbl_pub
        ID : 47
        F01 : 1.7976931348623157e+308
        SRC : t_dbl_pub
        ID : 48
        F01 : -9007199254740992.0
        SRC : t_dbl_pub
        ID : 49
        F01 : 9007199254740992.0
        SRC : t_dbl_priv_att
        ID : -40
        F01 : -2.9999999999999997e-308
        SRC : t_dbl_priv_att
        ID : -41
        F01 : 2.9999999999999997e-308
        SRC : t_dbl_priv_att
        ID : -42
        F01 : 1.7976931348623157e+308
        SRC : t_dbl_priv_att
        ID : -43
        F01 : -9007199254740992.0
        SRC : t_dbl_priv_att
        ID : -44
        F01 : 9007199254740992.0
        SRC : t_dbl_priv_trn
        ID : -50
        F01 : -2.9999999999999997e-308
        SRC : t_dbl_priv_trn
        ID : -51
        F01 : 2.9999999999999997e-308
        SRC : t_dbl_priv_trn
        ID : -52
        F01 : 1.7976931348623157e+308
        SRC : t_dbl_priv_trn
        ID : -53
        F01 : -9007199254740992.0
        SRC : t_dbl_priv_trn
        ID : -54
        F01 : 9007199254740992.0

        SRC : t_num_pub
        ID : 57
        F01 : -327.68
        SRC : t_num_pub
        ID : 58
        F01 : 327.67
        SRC : t_num_priv_att
        ID : -55
        F01 : -327.68
        SRC : t_num_priv_att
        ID : -56
        F01 : 327.67
        SRC : t_num_priv_trn
        ID : -59
        F01 : -327.68
        SRC : t_num_priv_trn
        ID : -60
        F01 : 327.67

        SRC : t_dec_pub
        ID : 63
        F01 : -327.68
        SRC : t_dec_pub
        ID : 64
        F01 : 327.67
        SRC : t_dec_priv_att
        ID : -61
        F01 : -327.68
        SRC : t_dec_priv_att
        ID : -62
        F01 : 327.67
        SRC : t_dec_priv_trn
        ID : -65
        F01 : -327.68
        SRC : t_dec_priv_trn
        ID : -66
        F01 : 327.67

        SRC : t_dfl_pub
        ID : 72
        F01 : -9.999999999999999999999999999999999E+6144
        SRC : t_dfl_pub
        ID : 73
        F01 : -1.0E-6143
        SRC : t_dfl_pub
        ID : 74
        F01 : 1.0E-6143
        SRC : t_dfl_pub
        ID : 75
        F01 : 9.999999999999999999999999999999999E+6144
        SRC : t_dfl_pub
        ID : 76
        F01 : 0E-6144
        SRC : t_dfl_priv_att
        ID : -67
        F01 : -9.999999999999999999999999999999999E+6144
        SRC : t_dfl_priv_att
        ID : -68
        F01 : -1.0E-6143
        SRC : t_dfl_priv_att
        ID : -69
        F01 : 1.0E-6143
        SRC : t_dfl_priv_att
        ID : -70
        F01 : 9.999999999999999999999999999999999E+6144
        SRC : t_dfl_priv_att
        ID : -71
        F01 : 0E-6144
        SRC : t_dfl_priv_trn
        ID : -77
        F01 : -9.999999999999999999999999999999999E+6144
        SRC : t_dfl_priv_trn
        ID : -78
        F01 : -1.0E-6143
        SRC : t_dfl_priv_trn
        ID : -79
        F01 : 1.0E-6143
        SRC : t_dfl_priv_trn
        ID : -80
        F01 : 9.999999999999999999999999999999999E+6144
        SRC : t_dfl_priv_trn
        ID : -81
        F01 : 0E-6144

        SRC : t_dat_pub
        ID : 83
        F01 : 2004-02-29
        SRC : t_dat_priv_att
        ID : -82
        F01 : 2004-02-29
        SRC : t_dat_priv_trn
        ID : -84
        F01 : 2004-02-29

        SRC : t_tim_pub
        ID : 86
        F01 : 01:02:03.456000
        SRC : t_tim_priv_att
        ID : -85
        F01 : 01:02:03.456000
        SRC : t_tim_priv_trn
        ID : -87
        F01 : 01:02:03.456000

        SRC : t_tms_pub
        ID : 89
        F01 : 2004-02-29 01:02:03.456000
        SRC : t_tms_priv_att
        ID : -88
        F01 : 2004-02-29 01:02:03.456000
        SRC : t_tms_priv_trn
        ID : -90
        F01 : 2004-02-29 01:02:03.456000

        SRC : t_tmz_pub
        ID : 92
        F01 : 01:02:03.456000
        SRC : t_tmz_priv_att
        ID : -91
        F01 : 01:02:03.456000
        SRC : t_tmz_priv_trn
        ID : -93
        F01 : 01:02:03.456000

        SRC : t_tsz_pub
        ID : 95
        F01 : 2004-02-29 01:02:03.456000+06:30
        SRC : t_tsz_priv_att
        ID : -94
        F01 : 2004-02-29 01:02:03.456000+06:30
        SRC : t_tsz_priv_trn
        ID : -96
        F01 : 2004-02-29 01:02:03.456000+06:30

        SRC : t_vchr_utf8_regular_pub
        ID : 98
        F01 : შობას გილოცავთ
        SRC : t_vchr_utf8_regular_priv_att
        ID : -97
        F01 : შობას გილოცავთ
        SRC : t_vchr_utf8_regular_priv_trn
        ID : -99
        F01 : შობას გილოცავთ

        SRC : t_vchr_utf8_ci_ai_pub
        ID : 101
        F01 : Շնորհավոր Սուրբ Ծնունդ
        SRC : t_vchr_utf8_ci_ai_priv_att
        ID : -100
        F01 : Շնորհավոր Սուրբ Ծնունդ
        SRC : t_vchr_utf8_ci_ai_priv_trn
        ID : -102
        F01 : Շնորհավոր Սուրբ Ծնունդ

        SRC : t_vchr_iso8859_1_da_da_pub
        ID : 104
        F01 : Børn får søde gærøl
        SRC : t_vchr_iso8859_1_da_da_priv_att
        ID : -103
        F01 : Børn får søde gærøl
        SRC : t_vchr_iso8859_1_da_da_priv_trn
        ID : -105
        F01 : Børn får søde gærøl

        SRC : t_vchr_iso8859_1_de_de_pub
        ID : 107
        F01 : Müßiggänger müssen süße Äpfel grüßen
        SRC : t_vchr_iso8859_1_de_de_priv_att
        ID : -106
        F01 : Müßiggänger müssen süße Äpfel grüßen
        SRC : t_vchr_iso8859_1_de_de_priv_trn
        ID : -108
        F01 : Müßiggänger müssen süße Äpfel grüßen

        SRC : t_vchr_iso8859_1_fr_fr_pub
        ID : 110
        F01 : L'été, là-bas, ç'a été délicieux
        SRC : t_vchr_iso8859_1_fr_fr_priv_att
        ID : -109
        F01 : L'été, là-bas, ç'a été délicieux
        SRC : t_vchr_iso8859_1_fr_fr_priv_trn
        ID : -111
        F01 : L'été, là-bas, ç'a été délicieux

        SRC : t_blb_utf8_regular_pub
        ID : 113
        F01 : შობას გილოცავთ
        SRC : t_blb_utf8_regular_priv_att
        ID : -112
        F01 : შობას გილოცავთ
        SRC : t_blb_utf8_regular_priv_trn
        ID : -114
        F01 : შობას გილოცავთ

        SRC : t_blb_utf8_ci_ai_pub
        ID : 116
        F01 : Շնորհավոր Սուրբ Ծնունդ
        SRC : t_blb_utf8_ci_ai_priv_att
        ID : -115
        F01 : Շնորհավոր Սուրբ Ծնունդ
        SRC : t_blb_utf8_ci_ai_priv_trn
        ID : -117
        F01 : Շնորհավոր Սուրբ Ծնունդ
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
