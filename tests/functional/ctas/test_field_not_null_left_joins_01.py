#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/e26e3e582663f91bfb37f0ce28dd9063ef50e3d3
TITLE:       CTAS. Nullability in case when column content is gathered from right part of OUTER join (which always may return null)
DESCRIPTION:
NOTES:
    [20.07.2026] pzotov
    See also: https://groups.google.com/g/firebird-devel/c/0a92QbfakP4/m/IioULnLRBAAJ
    Checked on 6.0.0.2081-3217f44
"""

import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_script = f"""
        set bail on;
        set list on;
        set autoterm on;
        commit;

        create domain dm_int_nullable int;
        create domain dm_int_nn int not null;
        create domain dm_df34_nn decfloat(34) not null;
        commit;

        set term ^;
        create procedure sa_sp_factor(i smallint) returns(o dm_df34_nn) as
        begin
            if ( i > 1 ) then
                o = i * (select o from sa_sp_factor( :i - 1 ));
            else
                o = i;
            suspend;
        end
        ^
        create function sa_fn_factor(i smallint) returns dm_df34_nn as
        begin
            if ( i > 1 ) then
                return i * sa_fn_factor( i-1 );
            else
                return i;
        end
        ^
        create package pg_test as
        begin
            procedure pg_sp_factor(i smallint) returns (o dm_df34_nn);
            function pg_fn_factor(i smallint) returns dm_df34_nn;
        end
        ^
        create package body pg_test as
        begin
            procedure pg_sp_factor(i smallint) returns(o dm_df34_nn) as
            begin
                if ( i > 1 ) then
                    o = i * (select o from pg_sp_factor( :i - 1 ));
                else
                    o = i;
                suspend;
            end

            function pg_fn_factor(i smallint) returns dm_df34_nn as
            begin
                if ( i > 1 ) then
                    return i * pg_fn_factor( i-1 );
                else
                    return i;
            end
        end
        ^
        set term ;^
        commit;

        create table tbase (
            fld_not_null_explicit int not null
           ,fld_not_null_owr_domain dm_int_nullable not null
           ,fld_not_null_via_domain dm_int_nn
        );
         
        create table ctas_test as(
            select
                b.fld_not_null_explicit as lj_fld_not_null_explicit
               ,b.fld_not_null_owr_domain as lj_fld_not_null_owr_domain
               ,b.fld_not_null_via_domain as lj_fld_not_null_via_domain
               ,(
                    with recursive
                    r1 as (
                        select 1 i, cast(1 as decfloat(34)) f from rdb$database
                        UNION ALL
                        select r.i+1, r.f * (r.i+1) from r1 as r where r.i < 1024
                    )
                    select max(r1.f) from r1
                ) as subq_factorial_recur
               ,(select p.o from sa_sp_factor(1000) as p) as subq_sa_factor_sp
               ,sa_fn_factor(1000) as subq_sa_factor_fn
               ,(select p.o from pg_test.pg_sp_factor(1000) as p) as subq_pg_factor_sp
               ,pg_test.pg_fn_factor(1000) as subq_pg_factor_fn
            from rdb$database d
            left join tbase b on 1=1
        ) with no data;
        commit;
    
        select
            rf.rdb$field_name as rf_fld_name
            ,rf.rdb$null_flag as rf_not_null
        from rdb$relation_fields rf
        where rf.rdb$relation_name = upper('CTAS_TEST')
        order by rf.rdb$field_position
        ;
        commit;
    """

    act.expected_stdout = """
        RF_FLD_NAME LJ_FLD_NOT_NULL_EXPLICIT
        RF_NOT_NULL <null>
        RF_FLD_NAME LJ_FLD_NOT_NULL_OWR_DOMAIN
        RF_NOT_NULL <null>
        RF_FLD_NAME LJ_FLD_NOT_NULL_VIA_DOMAIN
        RF_NOT_NULL <null>
        RF_FLD_NAME SUBQ_FACTORIAL_RECUR
        RF_NOT_NULL <null>
        RF_FLD_NAME SUBQ_SA_FACTOR_SP
        RF_NOT_NULL <null>
        RF_FLD_NAME SUBQ_SA_FACTOR_FN
        RF_NOT_NULL <null>
        RF_FLD_NAME SUBQ_PG_FACTOR_SP
        RF_NOT_NULL <null>
        RF_FLD_NAME SUBQ_PG_FACTOR_FN
        RF_NOT_NULL <null>
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
