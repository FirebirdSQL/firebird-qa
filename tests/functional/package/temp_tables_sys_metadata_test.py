#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8974
TITLE:       Temporary tables in packages (#8974) - get system metadata
DESCRIPTION:
    Test verifies that packaged temporary tables add package ownership and visibility information to system metadata.
    See the section "System metadata changes" in the doc/sql.extensions/README.packaged_temporary_tables.md
    In order to see info in mon$ tables test executes procedure 'sp_run_dml' which does INSERT in both pub and priv tables.
NOTES:
    [31.05.2026] pzotov
    Currently only INSERTs seems to be avaliable for DML in the unit which tries to run DML in the packages temp tables,
    see: https://groups.google.com/g/firebird-devel/c/IGAsQtQ5cFM/m/vEeqrVspAwAJ
    Checked on 6.0.0.1976.

    [02.06.2026] pzotov
    Before 01.06.2026 regression did exist: private packaged routine could be invoked from outer code,
    see: https://groups.google.com/g/firebird-devel/c/8Cu7J8pD_M4
    It has been fixed in 12b2158d (access restrictions to private routines in packages): procedure 'sp_run_dml'
    now must be specified both in head and body of package if we want to invoke it.
    Checked on 6.0.0.1978-12b2158.
"""
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db')

PKG_PUBL_TABLE = 't_pub'
PKG_PRIV_TABLE = 't_priv'

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    init_script = f"""
        set autoterm on;
        create or alter function fn_get_type_name(a_type smallint, a_subtype smallint) returns varchar(2048) as
            declare ftype varchar(2048);
        begin
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
                        , 26, 'int128'
                        , 27, 'double precision' -- also for numeric and decimal, both with size >= 10, if sql_dialect = 1
                        , 28, 'time with time zone'
                        , 29, 'timestamp with time zone'
                        , 35, 'timestamp without time zone'
                        , 37, decode(coalesce(a_subtype,0),  0, 'varchar',              1, 'varbinary', 'unknown')
                        ,261, decode(coalesce(a_subtype,0),  0, 'blob sub_type binary', 1, 'blob sub_type text', 'unknown')
                      );
            if (ftype = 'unknown') then
                ftype = ftype || '__type_'  || coalesce(a_type, '[null]') || '__subtype_' || coalesce(a_subtype, '[null]');
            return ftype;
        end
        ;
        create or alter package pg_test as
        begin
            temporary table {PKG_PUBL_TABLE}(id int, f01 int) on commit preserve rows unique index {PKG_PUBL_TABLE}_unq(id);
            -- fixed in 12b2158d (access restrictions to private routines in packages):
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
            index {PKG_PRIV_TABLE}_unq(
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
            ;
            procedure sp_run_dml as
                declare v int;
            begin
                insert into {PKG_PUBL_TABLE}(id, f01) values(1, 1);

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

                -- UPDATE/DELETE currently not avaliable, see:
                -- https://groups.google.com/g/firebird-devel/c/IGAsQtQ5cFM/m/vEeqrVspAwAJ

                --update {PKG_PUBL_TABLE} set f01 = f01+1 order by id rows 1;
                --delete from {PKG_PUBL_TABLE} order by id rows 1;
                --update {PKG_PRIV_TABLE} set tboo = not tboo order by tboo rows 1;
                --delete from {PKG_PRIV_TABLE} order by tboo rows 1;
            end
        end
        ;
        commit;

        create view v_get_packaged_table_metadata as
            select
                 r.rdb$package_name as pkg_name
                ,r.rdb$relation_name as pkg_tab_name
                ,r.rdb$private_flag as priv_flag
                ,rf.rdb$field_name as pkg_tab_fld_name
                ,upper(fn_get_type_name(f.rdb$field_type, f.rdb$field_sub_type)) as pkg_tab_fld_type
                ,ri.rdb$index_name as pkg_idx_name
                ,ri.rdb$unique_flag as pkg_idx_uniq
                ,decode(ri.rdb$index_type, 0, 'ASCEND', 1, 'DESCEND', '???') as pkg_idx_dir
                ,rs.rdb$field_position as pkg_idx_fld_pos
                ,rs.rdb$field_name as pkg_idx_fld_name
            from rdb$relations r
            join rdb$relation_fields rf
                on r.rdb$package_name = rf.rdb$package_name
                   and r.rdb$relation_name = rf.rdb$relation_name
            join rdb$fields f on rf.rdb$field_source = f.rdb$field_name
            left join rdb$indices ri
                on r.rdb$package_name = ri.rdb$package_name
                   and r.rdb$relation_name = ri.rdb$relation_name
            left join rdb$index_segments rs
                on r.rdb$package_name = rs.rdb$package_name
                   and ri.rdb$index_name = rs.rdb$index_name
            where r.rdb$relation_name in( upper('{PKG_PRIV_TABLE}'), upper('{PKG_PUBL_TABLE}') )
            order by pkg_tab_name, pkg_idx_name, pkg_idx_fld_pos
        ;

        create view v_get_packaged_table_mon_info as
            select
               t.mon$schema_name
               ,t.mon$table_name
               ,r.mon$record_inserts
               ,r.mon$record_updates
               ,r.mon$record_deletes
               ,r.mon$record_backouts
               ,r.mon$record_purges
               ,r.mon$record_expunges
               ,r.mon$record_seq_reads
               ,r.mon$record_idx_reads
            from
               mon$record_stats r
               join mon$table_stats t on r.mon$stat_id = t.mon$record_stat_id
               join mon$attachments a on t.mon$stat_id = a.mon$stat_id
            where
               a.mon$attachment_id = current_connection
               and t.mon$package_name = upper('pg_test')
        ;
    """
    act.isql(switches = ['-q'], input = init_script, combine_output = True)
    assert act.clean_stdout == '' and act.return_code == 0
    act.reset()

    with act.db.connect() as con_dba:
        cur_dba = con_dba.cursor()

        print('Check RDB-tables:')
        cur_dba.execute('select * from v_get_packaged_table_metadata')
        ccol=cur_dba.description
        for r in cur_dba:
            for i in range(0,len(ccol)):
                print( ccol[i][0],':', r[i])
        #-----------------------------------------------------

        cur_dba.callproc('pg_test.sp_run_dml')
        print('Check MON-info:')
        cur_dba.execute("select * from v_get_packaged_table_mon_info")
        ccol=cur_dba.description
        for r in cur_dba:
            for i in range(0,len(ccol)):
                print( ccol[i][0],':', r[i])

    act.expected_stdout = f"""

        Check RDB-tables:

        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : TBOO
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 1
        PKG_IDX_FLD_NAME : I016
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 2
        PKG_IDX_FLD_NAME : I032
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 3
        PKG_IDX_FLD_NAME : I064
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 4
        PKG_IDX_FLD_NAME : I128
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 5
        PKG_IDX_FLD_NAME : FFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 6
        PKG_IDX_FLD_NAME : FDBL
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 7
        PKG_IDX_FLD_NAME : XNUM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 8
        PKG_IDX_FLD_NAME : XDEC
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 9
        PKG_IDX_FLD_NAME : DFLT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 10
        PKG_IDX_FLD_NAME : TDAT
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 11
        PKG_IDX_FLD_NAME : TTIM
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 12
        PKG_IDX_FLD_NAME : TTMS
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 13
        PKG_IDX_FLD_NAME : TTMZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 14
        PKG_IDX_FLD_NAME : TTSZ
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TBOO
        PKG_TAB_FLD_TYPE : BOOLEAN
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I016
        PKG_TAB_FLD_TYPE : SMALLINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I032
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I064
        PKG_TAB_FLD_TYPE : BIGINT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : I128
        PKG_TAB_FLD_TYPE : INT128
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FFLT
        PKG_TAB_FLD_TYPE : FLOAT
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : FDBL
        PKG_TAB_FLD_TYPE : DOUBLE PRECISION
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XNUM
        PKG_TAB_FLD_TYPE : NUMERIC
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : XDEC
        PKG_TAB_FLD_TYPE : DECIMAL
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : DFLT
        PKG_TAB_FLD_TYPE : DECFLOAT(34)
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TDAT
        PKG_TAB_FLD_TYPE : DATE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTIM
        PKG_TAB_FLD_TYPE : TIME WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMS
        PKG_TAB_FLD_TYPE : TIMESTAMP WITHOUT TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTMZ
        PKG_TAB_FLD_TYPE : TIME WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TTSZ
        PKG_TAB_FLD_TYPE : TIMESTAMP WITH TIME ZONE
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PRIV
        PRIV_FLAG : 1
        PKG_TAB_FLD_NAME : TUTF
        PKG_TAB_FLD_TYPE : VARCHAR
        PKG_IDX_NAME : T_PRIV_UNQ
        PKG_IDX_UNIQ : 0
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 15
        PKG_IDX_FLD_NAME : TUTF
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PUB
        PRIV_FLAG : 0
        PKG_TAB_FLD_NAME : ID
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PUB_UNQ
        PKG_IDX_UNIQ : 1
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : ID
        PKG_NAME : PG_TEST
        PKG_TAB_NAME : T_PUB
        PRIV_FLAG : 0
        PKG_TAB_FLD_NAME : F01
        PKG_TAB_FLD_TYPE : INTEGER
        PKG_IDX_NAME : T_PUB_UNQ
        PKG_IDX_UNIQ : 1
        PKG_IDX_DIR : ASCEND
        PKG_IDX_FLD_POS : 0
        PKG_IDX_FLD_NAME : ID


        Check MON-info:

        MON$SCHEMA_NAME : PUBLIC
        MON$TABLE_NAME : T_PUB
        MON$RECORD_INSERTS : 1
        MON$RECORD_UPDATES : 0
        MON$RECORD_DELETES : 0
        MON$RECORD_BACKOUTS : 0
        MON$RECORD_PURGES : 0
        MON$RECORD_EXPUNGES : 0
        MON$RECORD_SEQ_READS : 0
        MON$RECORD_IDX_READS : 0
        MON$SCHEMA_NAME : PUBLIC
        MON$TABLE_NAME : T_PRIV
        MON$RECORD_INSERTS : 2
        MON$RECORD_UPDATES : 0
        MON$RECORD_DELETES : 0
        MON$RECORD_BACKOUTS : 0
        MON$RECORD_PURGES : 0
        MON$RECORD_EXPUNGES : 0
        MON$RECORD_SEQ_READS : 0
        MON$RECORD_IDX_READS : 0
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
