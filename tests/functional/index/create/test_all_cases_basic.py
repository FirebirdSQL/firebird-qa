#coding:utf-8

"""
ID:          n/a
TITLE:       CREATE INDEX: check all cases
DESCRIPTION:
    Check ability to create indices for all permitted cases and inability to do that for computed/blob/array columns.
    Content of RDB$ tables is verified in order to see data for just created index INSTEAD of usage 'SHOW' command.
    View 'v_index_info' is used to show all data related to indices.
    Its DDL differs for FB versions prior/ since 6.x (columns related to SQL schemas present for 6.x).
NOTES:
    [11.07.2025] pzotov
    This test replaces previously created ones with names: test_01.py ... test_10.py
    All these tests has been marked to be SKIPPED from execution.
    Checked on Checked on 6.0.0.909; 5.0.3.1668; 4.0.6.3214.
"""

import pytest
from firebird.qa import *

db = db_factory()
tmp_user = user_factory('db', name='tmp_indices_creator', password='123')

substitutions = [('[ \t]+', ' '), ('BLOB_ID_.*', 'BLOB_ID')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=4')
def test_1(act: Action, tmp_user: User):

    IDX_COND_SOURCE = '' if act.is_version('<5') else ',ri.rdb$condition_source as blob_id_idx_cond_source'
    SQL_SCHEMA_IDX = '' if act.is_version('<6') else ',ri.rdb$schema_name as ri_idx_schema_name'
    SQL_SCHEMA_FKEY = '' if act.is_version('<6') else ',ri.rdb$schema_name as ri_fk_schema_name'

    test_script = f"""
        set list on;
        set count on;
        set blob all;
        create view v_index_info as
        select
             ri.rdb$index_id as ri_idx_id
            ,ri.rdb$index_name as ri_idx_name
            ,ri.rdb$relation_name as ri_rel_name
            ,ri.rdb$unique_flag as ri_idx_uniq
            ,ri.rdb$segment_count as ri_idx_segm_count
            ,ri.rdb$index_inactive as ri_idx_inactive
            ,ri.rdb$index_type as ri_idx_type
            ,ri.rdb$foreign_key as ri_idx_fkey
            ,ri.rdb$expression_source as blob_id_idx_expr
            ,ri.rdb$description as blob_id_idx_descr
            -- 5.x
            {IDX_COND_SOURCE}
            --  6.x
            {SQL_SCHEMA_IDX}
            {SQL_SCHEMA_FKEY}
            ,rs.rdb$field_name as rs_fld_name
            ,rs.rdb$field_position as rs_fld_pos
            ,rc.rdb$constraint_name as rc_constraint_name
            ,rc.rdb$constraint_type as rc_constraint_type
        from rdb$indices ri
        LEFT -- ::: NB: 'rdb$index_segments' has no records for COMPUTED-BY indices.
             join rdb$index_segments rs on ri.rdb$index_name = rs.rdb$index_name
        left join rdb$relation_constraints rc on ri.rdb$relation_name = rc.rdb$relation_name
        where coalesce(ri.rdb$system_flag,0) = 0 and ri.rdb$index_name starting with 'TEST_'
        order by ri.rdb$relation_name, ri.rdb$index_name, rs.rdb$field_position
        ;    
        commit;
        grant select on v_index_info to {tmp_user.name};
        commit;

        grant create table to user {tmp_user.name};
        grant alter any table to user {tmp_user.name};
        grant drop any table to user {tmp_user.name};
        commit;

        connect '{act.db.dsn}' user '{tmp_user.name}' password '{tmp_user.password}';

        -- create using simplest form:
        create table test(f01 int);
        create index test_f01 on test(f01);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        create table test(f02 int);
        create unique index test_f02 on test(f02);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check ability to use 'asc' keyword:
        create table test(f03 int);
        create asc index test_f03 on test(f03);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check ability to use 'ascending' keyword:
        create table test(f03 int);
        create ascending index test_f03 on test(f03);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check ability to use 'desc' keyword:
        create table test(f05 int);
        create desc index test_f05 on test(f05);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check ability to use 'descending' keyword:
        create table test(f06 int);
        create descending index test_f06 on test(f06);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check ability to create multi-column indices, asc and desc (NB: max 16 columns can be specified):
        create table test(g01 int, g02 int, g03 int, g04 int, g05 int, g06 int, g07 int, g08 int, g09 int, g10 int, g11 int, g12 int, g13 int, g14 int, g15 int, g16 int);
        create index test_compound_asc on test(g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14, g15, g16);
        create descending index test_compound_dec on test(g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14, g15, g16);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check ability to create inactive index
        create table test(f06 int);
        create index test_f06 inactive on test(f06);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check ability to create computed index
        create table test(f07 int);
        create index test_f07 on test computed by (f07 * f07);
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check ability to foreign key that refers to the PK from the same table (get index info tfor such FK)
        create table test(id int primary key using index test_pk, pid int references test using index test_fk);
        commit;
        select * from v_index_info;
        drop table test;
        -----------------------------------
        -- test that we can *not* create compound index with 17+ columns:
        create table test(
            f_000 smallint,
            f_001 smallint,
            f_002 smallint,
            f_003 smallint,
            f_004 smallint,
            f_005 smallint,
            f_006 smallint,
            f_007 smallint,
            f_008 smallint,
            f_009 smallint,
            f_010 smallint,
            f_011 smallint,
            f_012 smallint,
            f_013 smallint,
            f_014 smallint,
            f_015 smallint,
            f_016 smallint
        );
        create index test_too_many_keys on test(
            f_000,
            f_001,
            f_002,
            f_003,
            f_004,
            f_005,
            f_006,
            f_007,
            f_008,
            f_009,
            f_010,
            f_011,
            f_012,
            f_013,
            f_014,
            f_015,
            f_016
        );
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check that we can *not* create index on computed field
        create table test(id int, h01 computed by (id * id) );
        create index test_h01 on test( h01 );
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check that we can *not* create index on blob field
        create table test(id int, h02 blob);
        create index test_h02 on test( h02 );
        commit;
        select * from v_index_info;
        drop table test;
        ---------------------------------
        -- check that we can *not* create index on array field
        create table test(id int, h03 int[3,4]);
        create index test_h03 on test( h03 );
        commit;
        select * from v_index_info;
        drop table test;
    """

    test_script_5x = f"""
        create table test(k01 int);
        create index test_k01_partial on test(k01) where k01 = 1 or k01 = 2 or k01 is null;
        commit;
        select * from v_index_info;
        drop table test;
        -----------------------------------
        create table test(k02 int);
        create unique descending index test_k02_partial on test(k02) where k02 = 1 or k02 = 2 or k02 is null;
        commit;
        select * from v_index_info;
        drop table test;
        -----------------------------------
        create table test(k03 int, dt date);
        create index test_k03_partial inactive on test(k03) where dt = current_date;
        commit;
        select * from v_index_info;
        drop table test;
        -----------------------------------
        create table test(k04 int, dt date);
        create descending index test_k04_partial on test computed by (k04 * k04) where dt = current_date;
        commit;
        select * from v_index_info;
        drop table test;
        -----------------------------------
        create table test(k05 int, dt date);
        create descending index test_k05_partial on test computed by (k05 * k05) where dt = (select max(dt) from test);
        commit;
        select * from v_index_info;
        drop table test;
        -----------------------------------
        create table test(k06 int, dt computed by ( dateadd(k06 day to date '01.01.1970') ) );
        create descending index test_k06_partial on test computed by (k06 * k06) where dt = (select max(dt) from test);
        commit;
        select * from v_index_info;
        drop table test;
    """

    if act.is_version('<5'):
        pass
    else:
        test_script += test_script_5x

    expected_stdout_4x = """
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F01
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F02
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F02
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F03
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F03
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F03
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F03
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F05
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F05
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F06
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F06
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G02
        RS_FLD_POS 1
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G03
        RS_FLD_POS 2
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G04
        RS_FLD_POS 3
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G05
        RS_FLD_POS 4
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G06
        RS_FLD_POS 5
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G07
        RS_FLD_POS 6
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G08
        RS_FLD_POS 7
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G09
        RS_FLD_POS 8
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G10
        RS_FLD_POS 9
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G11
        RS_FLD_POS 10
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G12
        RS_FLD_POS 11
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G13
        RS_FLD_POS 12
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G14
        RS_FLD_POS 13
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G15
        RS_FLD_POS 14
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G16
        RS_FLD_POS 15
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G02
        RS_FLD_POS 1
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G03
        RS_FLD_POS 2
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G04
        RS_FLD_POS 3
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G05
        RS_FLD_POS 4
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G06
        RS_FLD_POS 5
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G07
        RS_FLD_POS 6
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G08
        RS_FLD_POS 7
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G09
        RS_FLD_POS 8
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G10
        RS_FLD_POS 9
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G11
        RS_FLD_POS 10
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G12
        RS_FLD_POS 11
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G13
        RS_FLD_POS 12
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G14
        RS_FLD_POS 13
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G15
        RS_FLD_POS 14
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G16
        RS_FLD_POS 15
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 32
        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown - line 1, column 23
        -inactive
        Records affected: 0
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F07
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        (f07 * f07)
        BLOB_ID
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_1
        RC_CONSTRAINT_TYPE NOT NULL
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_2
        RC_CONSTRAINT_TYPE PRIMARY KEY
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_3
        RC_CONSTRAINT_TYPE FOREIGN KEY
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_1
        RC_CONSTRAINT_TYPE NOT NULL
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_2
        RC_CONSTRAINT_TYPE PRIMARY KEY
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_3
        RC_CONSTRAINT_TYPE FOREIGN KEY
        Records affected: 6
        Statement failed, SQLSTATE = 54011
        unsuccessful metadata update
        -too many keys defined for index TEST_TOO_MANY_KEYS
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX TEST_H01 failed
        -attempt to index COMPUTED BY column in INDEX TEST_H01
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX TEST_H02 failed
        - attempt to index BLOB column in INDEX TEST_H02
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX TEST_H03 failed
        - attempt to index array column in index TEST_H03
        Records affected: 0
    """
    
    expected_stdout_5x = """
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F01
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F02
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F02
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F03
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F03
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F03
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F03
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F05
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F05
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F06
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME F06
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G02
        RS_FLD_POS 1
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G03
        RS_FLD_POS 2
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G04
        RS_FLD_POS 3
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G05
        RS_FLD_POS 4
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G06
        RS_FLD_POS 5
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G07
        RS_FLD_POS 6
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G08
        RS_FLD_POS 7
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G09
        RS_FLD_POS 8
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G10
        RS_FLD_POS 9
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G11
        RS_FLD_POS 10
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G12
        RS_FLD_POS 11
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G13
        RS_FLD_POS 12
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G14
        RS_FLD_POS 13
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G15
        RS_FLD_POS 14
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G16
        RS_FLD_POS 15
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G02
        RS_FLD_POS 1
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G03
        RS_FLD_POS 2
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G04
        RS_FLD_POS 3
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G05
        RS_FLD_POS 4
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G06
        RS_FLD_POS 5
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G07
        RS_FLD_POS 6
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G08
        RS_FLD_POS 7
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G09
        RS_FLD_POS 8
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G10
        RS_FLD_POS 9
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G11
        RS_FLD_POS 10
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G12
        RS_FLD_POS 11
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G13
        RS_FLD_POS 12
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G14
        RS_FLD_POS 13
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G15
        RS_FLD_POS 14
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME G16
        RS_FLD_POS 15
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 32
        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown - line 1, column 23
        -inactive
        Records affected: 0
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F07
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        (f07 * f07)
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_1
        RC_CONSTRAINT_TYPE NOT NULL
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_2
        RC_CONSTRAINT_TYPE PRIMARY KEY
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_3
        RC_CONSTRAINT_TYPE FOREIGN KEY
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_1
        RC_CONSTRAINT_TYPE NOT NULL
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_2
        RC_CONSTRAINT_TYPE PRIMARY KEY
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_3
        RC_CONSTRAINT_TYPE FOREIGN KEY
        Records affected: 6
        Statement failed, SQLSTATE = 54011
        unsuccessful metadata update
        -too many keys defined for index TEST_TOO_MANY_KEYS
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX TEST_H01 failed
        -attempt to index COMPUTED BY column in INDEX TEST_H01
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX TEST_H02 failed
        - attempt to index BLOB column in INDEX TEST_H02
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX TEST_H03 failed
        - attempt to index array column in index TEST_H03
        Records affected: 0
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K01_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        where k01 = 1 or k01 = 2 or k01 is null
        RS_FLD_NAME K01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K02_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        where k02 = 1 or k02 = 2 or k02 is null
        RS_FLD_NAME K02
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown - line 1, column 31
        -inactive
        Records affected: 0
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K04_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        (k04 * k04)
        BLOB_ID
        BLOB_ID
        where dt = current_date
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K05_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        (k05 * k05)
        BLOB_ID
        BLOB_ID
        where dt = (select max(dt) from test)
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K06_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        (k06 * k06)
        BLOB_ID
        BLOB_ID
        where dt = (select max(dt) from test)
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
    """

    expected_stdout_6x = """
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F01
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME F01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F02
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME F02
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F03
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME F03
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F03
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME F03
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F05
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME F05
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F06
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME F06
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G02
        RS_FLD_POS 1
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G03
        RS_FLD_POS 2
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G04
        RS_FLD_POS 3
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G05
        RS_FLD_POS 4
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G06
        RS_FLD_POS 5
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G07
        RS_FLD_POS 6
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G08
        RS_FLD_POS 7
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G09
        RS_FLD_POS 8
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G10
        RS_FLD_POS 9
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G11
        RS_FLD_POS 10
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G12
        RS_FLD_POS 11
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G13
        RS_FLD_POS 12
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G14
        RS_FLD_POS 13
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G15
        RS_FLD_POS 14
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 1
        RI_IDX_NAME TEST_COMPOUND_ASC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G16
        RS_FLD_POS 15
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G02
        RS_FLD_POS 1
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G03
        RS_FLD_POS 2
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G04
        RS_FLD_POS 3
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G05
        RS_FLD_POS 4
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G06
        RS_FLD_POS 5
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G07
        RS_FLD_POS 6
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G08
        RS_FLD_POS 7
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G09
        RS_FLD_POS 8
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G10
        RS_FLD_POS 9
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G11
        RS_FLD_POS 10
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G12
        RS_FLD_POS 11
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G13
        RS_FLD_POS 12
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G14
        RS_FLD_POS 13
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G15
        RS_FLD_POS 14
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        RI_IDX_ID 2
        RI_IDX_NAME TEST_COMPOUND_DEC
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 16
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME G16
        RS_FLD_POS 15
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 32
        RI_IDX_ID <null>
        RI_IDX_NAME TEST_F06
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 1
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME F06
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_F07
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        (f07 * f07)
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_1
        RC_CONSTRAINT_TYPE NOT NULL
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_2
        RC_CONSTRAINT_TYPE PRIMARY KEY
        RI_IDX_ID 2
        RI_IDX_NAME TEST_FK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY TEST_PK
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME PID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_3
        RC_CONSTRAINT_TYPE FOREIGN KEY
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_1
        RC_CONSTRAINT_TYPE NOT NULL
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_2
        RC_CONSTRAINT_TYPE PRIMARY KEY
        RI_IDX_ID 1
        RI_IDX_NAME TEST_PK
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE <null>
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME ID
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME INTEG_3
        RC_CONSTRAINT_TYPE FOREIGN KEY
        Records affected: 6
        Statement failed, SQLSTATE = 54011
        unsuccessful metadata update
        -too many keys defined for index "PUBLIC"."TEST_TOO_MANY_KEYS"
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX "PUBLIC"."TEST_H01" failed
        -attempt to index COMPUTED BY column in INDEX "PUBLIC"."TEST_H01"
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX "PUBLIC"."TEST_H02" failed
        - attempt to index BLOB column in INDEX "PUBLIC"."TEST_H02"
        Records affected: 0
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -CREATE INDEX "PUBLIC"."TEST_H03" failed
        - attempt to index array column in index "PUBLIC"."TEST_H03"
        Records affected: 0
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K01_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        where k01 = 1 or k01 = 2 or k01 is null
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME K01
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K02_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 1
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        where k02 = 1 or k02 = 2 or k02 is null
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME K02
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID <null>
        RI_IDX_NAME TEST_K03_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 1
        RI_IDX_INACTIVE 1
        RI_IDX_TYPE 0
        RI_IDX_FKEY <null>
        BLOB_ID
        BLOB_ID
        BLOB_ID
        where dt = current_date
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME K03
        RS_FLD_POS 0
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K04_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        (k04 * k04)
        BLOB_ID
        BLOB_ID
        where dt = current_date
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K05_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        (k05 * k05)
        BLOB_ID
        BLOB_ID
        where dt = (select max(dt) from test)
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
        RI_IDX_ID 1
        RI_IDX_NAME TEST_K06_PARTIAL
        RI_REL_NAME TEST
        RI_IDX_UNIQ 0
        RI_IDX_SEGM_COUNT 0
        RI_IDX_INACTIVE 0
        RI_IDX_TYPE 1
        RI_IDX_FKEY <null>
        BLOB_ID
        (k06 * k06)
        BLOB_ID
        BLOB_ID
        where dt = (select max(dt) from test)
        RI_IDX_SCHEMA_NAME PUBLIC
        RI_FK_SCHEMA_NAME PUBLIC
        RS_FLD_NAME <null>
        RS_FLD_POS <null>
        RC_CONSTRAINT_NAME <null>
        RC_CONSTRAINT_TYPE <null>
        Records affected: 1
    """

    act.expected_stdout = expected_stdout_4x if act.is_version('<5') else expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

