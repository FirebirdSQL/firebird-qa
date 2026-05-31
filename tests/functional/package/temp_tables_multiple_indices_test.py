#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/89760a089690bca306c3c8b87d41f7269c8c4199
TITLE:       Temporary tables in packages (#8974) - multiple indices
DESCRIPTION:
    Test verifies that one may to create multiple indices for PTT (Packaged Temporary Table).
    For private PTT we only try to create N indices (each is compound and consists of 16 columns).
    For public PTT we do the same plus prepare queries that must show explained plans with usage
    of every created index (see `........-> Index "PUBLIC"."PG_TEST"."T_PUB_nn" Full Scan`).
NOTES:
    [01.06.2026] pzotov
    NB: private PTT currently is not accessible via ES from packaged units, see:
    https://groups.google.com/g/firebird-devel/c/reLukwY2ylY/m/0psTRj54AwAJ

    Checked on 6.0.0.1976-89760a0.
"""
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db')

PKG_PUBL_TABLE = 't_pub'
PKG_PRIV_TABLE = 't_priv'

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    init_script = f"""
        set autoterm on;
        create or alter package pg_test as
        begin
            temporary table {PKG_PUBL_TABLE}(
                 tboo boolean
                ,i016 smallint
                ,i032 int
                ,i064 bigint
                ,i128 int128
                ,fflt float
                ,fdbl double precision
                ,xnum numeric(2,2)
                ,xdec decimal(2,2)
                ,dflt decfloat
                ,tdat date
                ,ttim time
                ,ttms timestamp
                ,ttmz time with time zone
                ,ttsz timestamp with time zone
                ,tutf varchar(255) character set utf8
            ) on commit preserve rows
            index {PKG_PUBL_TABLE}_01(
                 tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
            )
            index {PKG_PUBL_TABLE}_02(
                 i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
            )
            index {PKG_PUBL_TABLE}_03(
                 i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
            )
            index {PKG_PUBL_TABLE}_04(
                 i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
            )
            index {PKG_PUBL_TABLE}_05(
                 i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
            )
            index {PKG_PUBL_TABLE}_06(
                 fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
            )
            index {PKG_PUBL_TABLE}_07(
                 fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
            )
            index {PKG_PUBL_TABLE}_08(
                 xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
            )
            index {PKG_PUBL_TABLE}_09(
                 xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
            )
            index {PKG_PUBL_TABLE}_10(
                 dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
            )
            index {PKG_PUBL_TABLE}_11(
                 tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
            )
            index {PKG_PUBL_TABLE}_12(
                 ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
            )
            index {PKG_PUBL_TABLE}_13(
                 ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
            )
            index {PKG_PUBL_TABLE}_14(
                 ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
            )
            index {PKG_PUBL_TABLE}_15(
                 ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
            )
            index {PKG_PUBL_TABLE}_16(
                 tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
            )
            ;

            procedure sp_run_dml;
        
        end
        ;
        recreate package body pg_test as
        begin
            temporary table {PKG_PRIV_TABLE}(
                 tboo boolean
                ,i016 smallint
                ,i032 int
                ,i064 bigint
                ,i128 int128
                ,fflt float
                ,fdbl double precision
                ,xnum numeric(2,2)
                ,xdec decimal(2,2)
                ,dflt decfloat
                ,tdat date
                ,ttim time
                ,ttms timestamp
                ,ttmz time with time zone
                ,ttsz timestamp with time zone
                ,tutf varchar(255) character set utf8
            ) on commit preserve rows
            index {PKG_PRIV_TABLE}_01(
                 tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
            )
            index {PKG_PRIV_TABLE}_02(
                 i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
            )
            index {PKG_PRIV_TABLE}_03(
                 i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
            )
            index {PKG_PRIV_TABLE}_04(
                 i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
            )
            index {PKG_PRIV_TABLE}_05(
                 i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
            )
            index {PKG_PRIV_TABLE}_06(
                 fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
            )
            index {PKG_PRIV_TABLE}_07(
                 fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
            )
            index {PKG_PRIV_TABLE}_08(
                 xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
            )
            index {PKG_PRIV_TABLE}_09(
                 xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
            )
            index {PKG_PRIV_TABLE}_10(
                 dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
            )
            index {PKG_PRIV_TABLE}_11(
                 tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
            )
            index {PKG_PRIV_TABLE}_12(
                 ttim
                ,ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
            )
            index {PKG_PRIV_TABLE}_13(
                 ttms
                ,ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
            )
            index {PKG_PRIV_TABLE}_14(
                 ttmz
                ,ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
            )
            index {PKG_PRIV_TABLE}_15(
                 ttsz
                ,tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
            )
            index {PKG_PRIV_TABLE}_16(
                 tutf
                ,tboo
                ,i016
                ,i032
                ,i064
                ,i128
                ,fflt
                ,fdbl
                ,xnum
                ,xdec
                ,dflt
                ,tdat
                ,ttim
                ,ttms
                ,ttmz
                ,ttsz
            )
            ;

            procedure sp_run_dml as
                declare v int;
            begin
                insert into {PKG_PRIV_TABLE}(
                     tboo
                    ,i016
                    ,i032
                    ,i064
                    ,i128
                    ,fflt
                    ,fdbl
                    ,xnum
                    ,xdec
                    ,dflt
                    ,tdat
                    ,ttim
                    ,ttms
                    ,ttmz
                    ,ttsz
                    ,tutf
                ) values(
                     false
                    ,-32768
                    ,-2147483648
                    ,-9223372036854775808
                    ,-170141183460469231731687303715884105728
                    ,3.40282346638e38
                    ,-3e-308
                    ,-327.68
                    ,-327.68
                    ,-9.999999999999999999999999999999999E6144
                    ,'29.02.2004'
                    ,'01:02:03.456'
                    ,'29.02.2004 01:02:03.456'
                    ,'01:02:03.456 Indian/Cocos'
                    ,'29.02.2004 01:02:03.456 Indian/Cocos'
                    ,'შობას გილოცავთ' -- georgian
                );

                insert into {PKG_PRIV_TABLE}(
                     tboo
                    ,i016
                    ,i032
                    ,i064
                    ,i128
                    ,fflt
                    ,fdbl
                    ,xnum
                    ,xdec
                    ,dflt
                    ,tdat
                    ,ttim
                    ,ttms
                    ,ttmz
                    ,ttsz
                    ,tutf
                ) values(
                     true
                    ,32767
                    ,2147483647
                    ,9223372036854775807
                    ,170141183460469231731687303715884105727
                    ,1.40129846432e-45
                    ,3e-308
                    ,327.67
                    ,327.67
                    ,-1.0E-6143
                    ,'28.02.2005'
                    ,'02:03:04.567'
                    ,'28.02.2005 02:03:04.567'
                    ,'02:03:04.567 Indian/Cocos'
                    ,'28.02.2005 02:03:04.567 Indian/Cocos'
                    ,'Շնորհավոր Սուրբ Ծնունդ' -- armenian
                );
                insert into {PKG_PRIV_TABLE} select * from {PKG_PRIV_TABLE}; --   4
                insert into {PKG_PRIV_TABLE} select * from {PKG_PRIV_TABLE}; --   8
                insert into {PKG_PRIV_TABLE} select * from {PKG_PRIV_TABLE}; --  16
                insert into {PKG_PRIV_TABLE} select * from {PKG_PRIV_TABLE}; --  32
                insert into {PKG_PRIV_TABLE} select * from {PKG_PRIV_TABLE}; --  64
                insert into {PKG_PRIV_TABLE} select * from {PKG_PRIV_TABLE}; -- 128
                insert into {PKG_PRIV_TABLE} select * from {PKG_PRIV_TABLE}; -- 256

                insert into {PKG_PUBL_TABLE} select * from {PKG_PRIV_TABLE};
            end
            
        end
        ;
        commit;
    """
    act.isql(switches = ['-q', '-pag', '999999'], input = init_script, combine_output = True)
    assert act.clean_stdout == '' and act.return_code == 0
    act.reset()

    ls = ['tboo', 'i016', 'i032', 'i064', 'i128', 'fflt', 'fdbl', 'xnum', 'xdec', 'dflt', 'tdat', 'ttim', 'ttms', 'ttmz', 'ttsz', 'tutf']

    qry_lst = [ f'select * from pg_test.{PKG_PUBL_TABLE} order by ' + ','.join(ls[i:] + ls[:i]) for i in range(len(ls)) ]

    qry_priv_lst = [ f'select * from pg_test.{PKG_PRIV_TABLE} order by ' + ','.join(ls[i:] + ls[:i]) for i in range(len(ls)) ]

    with act.db.connect() as con_dba:
        cur_dba = con_dba.cursor()
        cur_dba.callproc('pg_test.sp_run_dml')
        for q in qry_lst:
            print(q)
            ps, rs =  None, None
            try:
                ps = cur_dba.prepare(q)
                print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()

    act.expected_stdout = f"""
        select * from pg_test.t_pub order by tboo,i016,i032,i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_01" Full Scan
        select * from pg_test.t_pub order by i016,i032,i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_02" Full Scan
        select * from pg_test.t_pub order by i032,i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_03" Full Scan
        select * from pg_test.t_pub order by i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_04" Full Scan
        select * from pg_test.t_pub order by i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_05" Full Scan
        select * from pg_test.t_pub order by fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064,i128
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_06" Full Scan
        select * from pg_test.t_pub order by fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064,i128,fflt
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_07" Full Scan
        select * from pg_test.t_pub order by xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064,i128,fflt,fdbl
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_08" Full Scan
        select * from pg_test.t_pub order by xdec,dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064,i128,fflt,fdbl,xnum
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_09" Full Scan
        select * from pg_test.t_pub order by dflt,tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064,i128,fflt,fdbl,xnum,xdec
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_10" Full Scan
        select * from pg_test.t_pub order by tdat,ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064,i128,fflt,fdbl,xnum,xdec,dflt
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_11" Full Scan
        select * from pg_test.t_pub order by ttim,ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_12" Full Scan
        select * from pg_test.t_pub order by ttms,ttmz,ttsz,tutf,tboo,i016,i032,i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_13" Full Scan
        select * from pg_test.t_pub order by ttmz,ttsz,tutf,tboo,i016,i032,i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_14" Full Scan
        select * from pg_test.t_pub order by ttsz,tutf,tboo,i016,i032,i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_15" Full Scan
        select * from pg_test.t_pub order by tutf,tboo,i016,i032,i064,i128,fflt,fdbl,xnum,xdec,dflt,tdat,ttim,ttms,ttmz,ttsz
        Select Expression
        ....-> Table "PUBLIC"."PG_TEST"."T_PUB" Access By ID
        ........-> Index "PUBLIC"."PG_TEST"."T_PUB_16" Full Scan
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
